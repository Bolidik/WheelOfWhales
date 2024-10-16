import asyncio
import string
import os
import random

import aiohttp
import json

from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector
import cloudscraper
from better_proxy import Proxy
from urllib.parse import unquote

from faker import Faker
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered, FloodWait
from pyrogram.raw.functions.messages import RequestWebView
from datetime import datetime, timedelta, timezone

from bot.config import settings
from bot.utils import logger
from bot.exceptions import InvalidSession

from .headers import headers
from .agents import generate_random_user_agent


class Tapper:
    def __init__(self, tg_client: Client):
        self.session_name = tg_client.name
        self.tg_client = tg_client
        self.user_id = 0
        self.username = None
        self.url = 'https://clicker-api.crashgame247.io'

        self.session_ug_dict = self.load_user_agents() or []
        self.user_data = self.load_user_data()

        headers['User-Agent'] = self.check_user_agent()

    async def generate_random_user_agent(self):
        return generate_random_user_agent(device_type='android', browser_type='chrome')

    def save_user_agent(self):
        user_agents_file_name = "user_agents.json"

        if not any(session['session_name'] == self.session_name for session in self.session_ug_dict):
            user_agent_str = generate_random_user_agent()

            self.session_ug_dict.append({
                'session_name': self.session_name,
                'user_agent': user_agent_str})

            with open(user_agents_file_name, 'w') as user_agents:
                json.dump(self.session_ug_dict, user_agents, indent=4)

            logger.success(f"<light-yellow>{self.session_name}</light-yellow> | User agent saved successfully")

            return user_agent_str

    def load_user_agents(self):
        user_agents_file_name = "user_agents.json"

        try:
            with open(user_agents_file_name, 'r') as user_agents:
                session_data = json.load(user_agents)
                if isinstance(session_data, list):
                    return session_data

        except FileNotFoundError:
            logger.warning("User agents file not found, creating...")

        except json.JSONDecodeError:
            logger.warning("User agents file is empty or corrupted.")

        return []

    def check_user_agent(self):
        load = next(
            (session['user_agent'] for session in self.session_ug_dict if session['session_name'] == self.session_name),
            None)

        if load is None:
            return self.save_user_agent()

        return load

    def load_user_data(self):
        user_data_file_name = f"data/{self.session_name}.json"
        if not os.path.exists('data'):
            os.makedirs('data')

        try:
            with open(user_data_file_name, 'r') as user_data_file:
                return json.load(user_data_file)

        except FileNotFoundError:
            logger.warning(f"User data file for {self.session_name} not found, creating a new one...")
            return {"referred": None, "last_click_time": None, "last_sleep_time": None, "acknowledged": False, "squad_name": None, "in_squad": False}

        except json.JSONDecodeError:
            logger.warning(f"User data file for {self.session_name} is empty or corrupted. Creating a new one...")
            return {"referred": None, "last_click_time": None, "last_sleep_time": None, "acknowledged": False, "squad_name": None, "in_squad": False}

        except Exception as error:
            logger.error(f"An unexpected error occurred while loading user data for {self.session_name}: {error}")
            return {"referred": None, "last_click_time": None, "last_sleep_time": None, "acknowledged": False, "squad_name": None, "in_squad": False}

    def save_user_data(self):
        user_data_file_name = f"data/{self.session_name}.json"
        with open(user_data_file_name, 'w') as user_data_file:
            json.dump(self.user_data, user_data_file, indent=4)

    async def get_tg_web_data(self, proxy: str | None, http_client: aiohttp.ClientSession) -> str:
        if proxy:
            proxy = Proxy.from_str(proxy)
            proxy_dict = dict(
                scheme=proxy.protocol,
                hostname=proxy.host,
                port=proxy.port,
                username=proxy.login,
                password=proxy.password
            )
        else:
            proxy_dict = None

        self.tg_client.proxy = proxy_dict
        ref_param = settings.REF_ID if settings.REF_ID != '' else False
        if ref_param and not ref_param.endswith("pub"):
            self.user_data["referred"] = "gold"
        elif ref_param:
            self.user_data["referred"] = "regular"

        self.save_user_data()

        try:
            with_tg = True

            if not self.tg_client.is_connected:
                with_tg = False
                try:
                    await self.tg_client.connect()
                    start_command_found = False

                    async for message in self.tg_client.get_chat_history("WheelOfWhalesBot"):
                        if (message.text and message.text.startswith("/start")) or (message.caption and message.caption.startswith("/start")):
                            start_command_found = True
                            break

                    if start_command_found:
                        self.user_data["acknowledged"] = True
                        self.save_user_data()
                    else:
                        if ref_param:
                            await self.tg_client.send_message("WheelOfWhalesBot", f"/start {ref_param}")
                            if not ref_param.endswith("pub"):
                                logger.success(f"<light-yellow>{self.session_name}</light-yellow> | Referred by a <yellow>gold</yellow> ticket.")
                            else:
                                logger.success(f"<light-yellow>{self.session_name}</light-yellow> | Referred by a regular referral.")

                except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                    raise InvalidSession(self.session_name)

            while True:
                try:
                    peer = await self.tg_client.resolve_peer('WheelOfWhalesBot')
                    break
                except FloodWait as fl:
                    fls = fl.value

                    logger.warning(f"{self.session_name} | FloodWait {fl}")
                    logger.info(f"{self.session_name} | Sleep {fls}s")

                    await asyncio.sleep(fls + 3)

            web_view = await self.tg_client.invoke(RequestWebView(
                peer=peer,
                bot=peer,
                platform='android',
                from_bot_menu=False,
                url="https://clicker.crashgame247.io/"
            ))

            auth_url = web_view.url
            tg_web_data = unquote(
                string=unquote(
                    string=auth_url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0]))

            me = await self.tg_client.get_me()
            self.user_id = me.id
            self.username = me.username if me.username else ''
            if self.username == '':
                while True:
                    fake = Faker('en_US')

                    name_english = fake.name()
                    name_modified = name_english.replace(" ", "").lower()

                    random_letters = ''.join(random.choices(string.ascii_lowercase, k=random.randint(1, 7)))
                    final_name = name_modified + random_letters
                    status = await self.tg_client.set_username(final_name)
                    if status:
                        logger.info(f"<light-yellow>{self.session_name}</light-yellow> | Set username {final_name}")
                        break
                    else:
                        continue

            if with_tg is False:
                await self.tg_client.disconnect()

            return tg_web_data

        except InvalidSession as error:
            raise error

        except Exception as error:
            logger.error(f"<light-yellow>{self.session_name}</light-yellow> | Unknown error during Authorization: {error}")
            await asyncio.sleep(3)

    async def check_proxy(self, http_client: aiohttp.ClientSession, proxy: Proxy) -> None:
        try:
            response = await http_client.get(url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(5))
            ip = (await response.json()).get('origin')
            logger.info(f"<light-yellow>{self.session_name}</light-yellow> | Proxy IP: {ip}")
        except Exception as error:
            logger.error(f"<light-yellow>{self.session_name}</light-yellow> | Proxy: {proxy} | Error: {error}")

    async def login(self, http_client: aiohttp.ClientSession, init_data):
        params = dict(item.split('=') for item in init_data.split('&'))
        user_data = json.loads(unquote(params['user']))

        data = {
            "dataCheckChain": init_data,
            "initData": {
                "query_id": params['query_id'],
                "user": user_data,
                "auth_date": params['auth_date'],
                "hash": params['hash']
            }
        }

        resp = await http_client.post(f"{self.url}/user/sync", json=data)
        resp_json = await resp.json()

        token = resp_json.get("token")
        whitelisted = resp_json.get("user", {}).get("whitelisted")
        banned = resp_json.get("user", {}).get("isBanned")
        balance = resp_json.get("balance", {}).get("amount")
        streak = resp_json.get("meta", {}).get("dailyLoginStreak")
        last_login = resp_json.get("meta", {}).get("lastFirstDailyLoginAt")
        referrer = resp_json.get("referrerUsername")
        tribe = resp_json.get("user", {}).get("tribeId")

        return (token, whitelisted, banned, balance, streak, last_login, referrer, tribe)

    async def claim_daily_bonus(self, http_client, proxy):
        url = f"{self.url}/user/bonus/claim"
        
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'ru-RU,ru;q=0.9',
            'Authorization': http_client.headers.get('Authorization'),
            'Origin': 'https://clicker.crashgame247.io',
            'Priority': 'u=1, i',
            'Referer': 'https://clicker.crashgame247.io/',
            'Sec-Ch-Ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'Sec-Ch-Ua-Mobile': '?1',
            'Sec-Ch-Ua-Platform': '"Android"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': http_client.headers.get('User-Agent')
        }
        
        try:
            scraper = cloudscraper.create_scraper()

            proxies = {
                'http': proxy,
                'https': proxy,
            } if proxy else None

            response = scraper.patch(url, headers=headers, proxies=proxies)
            
            if response.status_code == 200:
                return True
            else:
                try:
                    error_data = response.json()
                    logger.error(f"<light-yellow>{self.session_name}</light-yellow> | Error when claiming the daily bonus: {error_data}")
                except json.JSONDecodeError:
                    logger.error(f"<light-yellow>{self.session_name}</light-yellow> | Failed to decode error response: {response.text}")
                
                if response.status_code == 500:
                    return False
        
        except cloudscraper.exceptions.CloudflareChallengeError as e:
            logger.error(f"{self.session_name} | Cloudflare challenge error occurred: {e}")
        except Exception as e:
            logger.error(f"{self.session_name} | Unexpected error: {str(e)}")

    async def send_clicks(self, http_client: aiohttp.ClientSession, click_count: int):
        clicks = {"clicks": click_count}
        try:
            async with http_client.put(
                f"{self.url}/meta/clicks", 
                json=clicks
            ) as response:
                if response.status == 200:
                    pass
                else:
                    logger.error(f"<light-yellow>{self.session_name}</light-yellow> | Failed with status: {response.status}")
                    try:
                        error_body = await response.text()
                        logger.error(f"<light-yellow>{self.session_name}</light-yellow> | Response body: {error_body}")
                    except Exception as e:
                        logger.error(f"<light-yellow>{self.session_name}</light-yellow> | Failed to read response body: {e}")
        except aiohttp.ClientError as e:
            logger.error(f"<light-yellow>{self.session_name}</light-yellow> | Client error occurred: {e}")
        except asyncio.TimeoutError:
            logger.error(f"<light-yellow>{self.session_name}</light-yellow> | Request timed out.")
        except Exception as e:
            logger.error(f"<light-yellow>{self.session_name}</light-yellow> | Unexpected error: {str(e)}")

    async def clicker(self, http_client: aiohttp.ClientSession):
        logger.success(f"<light-yellow>{self.session_name}</light-yellow> | AutoTapper started!")

        last_click_time = self.user_data.get("last_click_time")
        if last_click_time:
            last_click_time = datetime.strptime(last_click_time, "%Y-%m-%d %H:%M:%S.%f").replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) - last_click_time < timedelta(hours=1):
                logger.info(f"<light-yellow>{self.session_name}</light-yellow> | Sleep time not yet reached, waiting...")
                return

        clicks = [random.randint(1, 8) for _ in range(1000)]
        random.shuffle(clicks)

        total_clicks = 0
        total_time = 0

        intervals = [random.uniform(1, 2) for _ in clicks]
        total_time = sum(intervals)

        logger.success(f"<light-yellow>{self.session_name}</light-yellow> | Estimated clicking time: {total_time / 60:.2f} minutes")

        for click_count, interval in zip(clicks, intervals):
            await self.send_clicks(http_client=http_client, click_count=click_count)
            total_clicks += click_count

            self.user_data["last_click_time"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")
            self.save_user_data()

            await asyncio.sleep(interval)

            if total_clicks >= 1000:
                break

        sleep_time = random.randint(1100, 2000)  # Примерно от 18 до 33 минут
        self.user_data["last_sleep_time"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")
        self.save_user_data()

        logger.success(f"<light-yellow>{self.session_name}</light-yellow> | {total_clicks} clicks sent, sleeping for {sleep_time // 60} minutes.")
        
        await asyncio.sleep(sleep_time)

    async def get_squad_info(self, http_client, squad_name):
        try:
            response = await http_client.get(f"{self.url}/tribes/{squad_name}")
            response.raise_for_status()
            response_json = await response.json()
            return response_json
        except Exception as error:
            logger.error(f"<light-yellow>{self.session_name}</light-yellow> | Error getting squad info for {squad_name}: {error}")
            return None

    async def join_squad(self, squad_name, http_client, proxy):
        try:
            scraper = cloudscraper.create_scraper()

            proxies = {
                'http': proxy,
                'https': proxy,
            } if proxy else None

            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Accept-Language': 'ru-RU,ru;q=0.9',
                'Origin': 'https://clicker.crashgame247.io',
                'Referer': 'https://clicker.crashgame247.io/',
                'Sec-Ch-Ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
                'Sec-Ch-Ua-Mobile': '?1',
                'Sec-Ch-Ua-Platform': 'Android',
                "Authorization": http_client.headers.get('Authorization'),
                "User-Agent": http_client.headers.get('User-Agent')
            }

            response = scraper.post(
                f"https://clicker-api.crashgame247.io/tribes/{squad_name}/join",
                headers=headers,
                proxies=proxies
            )

            if response.status_code == 200:
                if response.text == 'true':
                    return True

                response_json = response.json()
                return response_json
            else:
                raise Exception(f"Failed to join squad. Status code: {response.status_code}, Message: {response.text}")

        except Exception as error:
            logger.error(f"<light-yellow>{self.session_name}</light-yellow> | Error joining squad {squad_name}: {error}")
            return None

    async def run(self, proxy: str | None) -> None:
        proxy_conn = ProxyConnector().from_url(proxy) if proxy else None
        http_client = CloudflareScraper(headers=headers, connector=proxy_conn)
        squad_name = settings.REF_ID if settings.REF_ID != '' else False

        if proxy:
            await self.check_proxy(http_client=http_client, proxy=proxy)

        init_data = await self.get_tg_web_data(proxy=proxy, http_client=http_client)
        token, whitelisted, banned, balance, streak, last_login, referrer, tribe = await self.login(http_client=http_client, init_data=init_data)
        
        logger.info(f"<light-yellow>{self.session_name}</light-yellow> | Balance: {balance}")
        http_client.headers["Authorization"] = f"Bearer {token}"

        await self.claim_daily_bonus(http_client=http_client, proxy=proxy)

        if not whitelisted:
            logger.warning(f"<light-yellow>{self.session_name}</light-yellow> | You are not whitelisted :(")
            return

        if banned:
            logger.warning(f"<light-yellow>{self.session_name}</light-yellow> | You are banned :(")
            return

        if self.user_data["referred"] == "gold" and not self.user_data["acknowledged"]:
            self.user_data["acknowledged"] = True
            self.save_user_data()
            if referrer:
                logger.success(f"<light-yellow>{self.session_name}</light-yellow> | Referred By: @{referrer}")

        if settings.AUTO_TAP:
            logger.info(f"<light-yellow>{self.session_name}</light-yellow> | Starting AutoTapper...")
            asyncio.create_task(self.clicker(http_client=http_client))

        if squad_name:
            if not tribe:
                if not self.user_data.get("in_squad", False):
                    squad_info = await self.get_squad_info(http_client=http_client, squad_name=settings.SQUAD_NAME)
                    if squad_info:
                        squad_name = squad_info.get("name")
                        if squad_name:
                            join = await self.join_squad(http_client=http_client, proxy=proxy, squad_name=settings.SQUAD_NAME)
                            if join:
                                logger.success(f"<light-yellow>{self.session_name}</light-yellow> | Successfully joined squad: {squad_name}")
                                self.user_data["squad_name"] = squad_name
                                self.user_data["in_squad"] = True
                                self.save_user_data()
                            else:
                                logger.error(f"<light-yellow>{self.session_name}</light-yellow> | Failed to join squad: {squad_name}")

        while True:
            try:
                if last_login is not None:
                    last_login_time = datetime.strptime(last_login, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
                else:
                    logger.error(f"<light-yellow>{self.session_name}</light-yellow> | Last login data is None (please restart the bot)")

                if datetime.now(timezone.utc) - last_login_time > timedelta(hours=24):
                    bonus = await self.claim_daily_bonus(http_client=http_client, proxy=proxy)
                    if bonus:
                        new_streak = streak + 1
                        logger.success(f"<light-yellow>{self.session_name}</light-yellow> | Daily bonus successfully claimed! Current streak: {new_streak}")

                logger.info(f"<light-yellow>{self.session_name}</light-yellow> | Going sleep 8h (This doesn't concern the AutoTapper)")

                await asyncio.sleep(8 * 3600)

            except InvalidSession as error:
                raise error

            except Exception as error:
                logger.error(f"{self.session_name} | Unknown error: {error} (Try restarting the bot..)")
                await asyncio.sleep(3)

async def run_tapper(tg_client: Client, proxy: str | None):
    try:
        await Tapper(tg_client=tg_client).run(proxy=proxy)
    except InvalidSession:
        logger.error(f"{tg_client.name} | Invalid Session")