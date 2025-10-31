#добро пожаловать на кровавую арену смерти

from base_plugin import BasePlugin, HookResult, HookStrategy
from typing import Any
from markdown_utils import parse_markdown
from client_utils import send_message, get_last_fragment, run_on_queue, EXTERNAL_NETWORK_QUEUE
from android_utils import log
import requests
from ui.settings import Switch, Divider, Text
from ui.alert import AlertDialogBuilder
from PIL import Image
import io, base64, os
from file_utils import get_files_dir, ensure_dir_exists, write_file, list_dir, read_file


__id__ = "dotastats"
__name__ = "DotaStats"
__description__ = "Информация о твоих последних матчах или о конкретном матче. Гайд в настройках\nProvides information about your last dota matches or about specific match. Guide in settings"
__author__ = "@a352642 | @kingley_the_lord"
__version__ = "7.39/1.1"
__icon__ = "dota_2/0"
__min_version__ = "12.1.1"

BASE_URL = "https://api.opendota.com/api/"
HEROES = {1: 'Anti-Mage', 2: 'Axe', 3: 'Bane', 4: 'Bloodseeker', 5: 'Crystal Maiden', 6: 'Drow Ranger', 7: 'Earthshaker', 8: 'Juggernaut', 9: 'Mirana', 10: 'Morphling', 11: 'Shadow Fiend', 12: 'Phantom Lancer', 13: 'Puck', 14: 'Pudge', 15: 'Razor', 16: 'Sand King', 17: 'Storm Spirit', 18: 'Sven', 19: 'Tiny', 20: 'Vengeful Spirit', 21: 'Windranger', 22: 'Zeus', 23: 'Kunkka', 25: 'Lina', 26: 'Lion', 27: 'Shadow Shaman', 28: 'Slardar', 29: 'Tidehunter', 30: 'Witch Doctor', 31: 'Lich', 32: 'Riki', 33: 'Enigma', 34: 'Tinker', 35: 'Sniper', 36: 'Necrophos', 37: 'Warlock', 38: 'Beastmaster', 39: 'Queen of Pain', 40: 'Venomancer', 41: 'Faceless Void', 42: 'Wraith King', 43: 'Death Prophet', 44: 'Phantom Assassin', 45: 'Pugna', 46: 'Templar Assassin', 47: 'Viper', 48: 'Luna', 49: 'Dragon Knight', 50: 'Dazzle', 51: 'Clockwerk', 52: 'Leshrac', 53: "Nature's Prophet", 54: 'Lifestealer', 55: 'Dark Seer', 56: 'Clinkz', 57: 'Omniknight', 58: 'Enchantress', 59: 'Huskar', 60: 'Night Stalker', 61: 'Broodmother', 62: 'Bounty Hunter', 63: 'Weaver', 64: 'Jakiro', 65: 'Batrider', 66: 'Chen', 67: 'Spectre', 68: 'Ancient Apparition', 69: 'Doom', 70: 'Ursa', 71: 'Spirit Breaker', 72: 'Gyrocopter', 73: 'Alchemist', 74: 'Invoker', 75: 'Silencer', 76: 'Outworld Destroyer', 77: 'Lycan', 78: 'Brewmaster', 79: 'Shadow Demon', 80: 'Lone Druid', 81: 'Chaos Knight', 82: 'Meepo', 83: 'Treant Protector', 84: 'Ogre Magi', 85: 'Undying', 86: 'Rubick', 87: 'Disruptor', 88: 'Nyx Assassin', 89: 'Naga Siren', 90: 'Keeper of the Light', 91: 'Io', 92: 'Visage', 93: 'Slark', 94: 'Medusa', 95: 'Troll Warlord', 96: 'Centaur Warrunner', 97: 'Magnus', 98: 'Timbersaw', 99: 'Bristleback', 100: 'Tusk', 101: 'Skywrath Mage', 102: 'Abaddon', 103: 'Elder Titan', 104: 'Legion Commander', 105: 'Techies', 106: 'Ember Spirit', 107: 'Earth Spirit', 108: 'Underlord', 109: 'Terrorblade', 110: 'Phoenix', 111: 'Oracle', 112: 'Winter Wyvern', 113: 'Arc Warden', 114: 'Monkey King', 119: 'Dark Willow', 120: 'Pangolier', 121: 'Grimstroke', 123: 'Hoodwink', 126: 'Void Spirit', 128: 'Snapfire', 129: 'Mars', 131: 'Ringmaster', 135: 'Dawnbreaker', 136: 'Marci', 137: 'Primal Beast', 138: 'Muerta', 145: 'Kez'}
GAME_MODES = {
  0: {"name": "",},
  1: {"name": "All pick",},
  2: {"name": "Captains mode",},
  3: {"name": "Random draft",},
  4: {"name": "Single draft",},
  5: {"name": "All random",},
  6: {"name": "Intro mode",},
  7: {"name": "Diretide",},
  8: {"name": "Reverse Captains mode",},
  9: {"name": "Greeviling",},
  10: {"name": "Tutorial",},
  11: {"name": "Mid only",},
  12: {"name": "Least Played mode",},
  13: {"name": "Limited heroes mode",},
  14: {"name": "Compendium",},
  15: {"name": "Custom",},
  16: {"name": "Captains draft",},
  17: {"name": "Balanced draft",},
  18: {"name": "Ability draft",},
  19: {"name": "Event mode",},
  20: {"name": "All random deathmatch",},
  21: {"name": "1v1 mid",},
  22: {"name": "All draft",},
  23: {"name": "Turbo",},
  24: {"name": "Mutation mode",},
  25: {"name": "Coaches challenge",}
}

def seconds_to_normal_time(secs):
    mins = secs//60
    secs = secs-mins*60
    return f"{mins}:{secs if secs > 9 else '0'+str(secs)}"

radiant_heroes_x = 19
dire_heroes_x = 1533
radiant_items_x = 224
dire_items_x = 946
radiant_aghan_scepter_x = 806
dire_aghan_scepter_x = 892
radiant_aghan_shard_x = 803
dire_aghan_shard_x = 889
heroes_y = [132, 249, 365, 482, 598]
items_y = [179, 295, 412, 528, 645]
aghan_scepter_y = items_y
aghan_shard_y = [216, 332, 449, 565, 682]
player_stats_y = [134, 250, 367, 484, 600]
radiant_stats_x = 223
radiant_networth_x = 753
dire_stats_x = 1510
dire_networth_x = 992
radiant_nicknames_x = 390
dire_nicknames_x = 1094

localize = {
    "always_send_images": {
        "ru": "Всегда отправлять изображения",
        "en": "Always send images"
    },
    "usage": {
        "ru": "Использование: .dotamatch <id_матча>\nили .dotaprofile <9_цифр_профиля>",
        "en": "Usage: .dotamatch <match_id>\nor .dotaprofile <9digit_profile_id>"
    },
    "match_not_found": {
        "ru": "Матч №{} не найден",
        "en": "Match №{} not found"
    },
    "radiant_victory": {
        "ru": "Победа сил Света",
        "en": "Radiant victory"
    },
    "dire_victory": {
        "ru": "Победа сил Тьмы",
        "en": "Dire victory"
    },
    "radiant": {
        "ru": "Силы Света",
        "en": "Radiant"
    },
    "dire": {
        "ru": "Силы Тьмы",
        "en": "Dire"
    },
    "invalid_id_profile": {
        "ru": "Неверный ID, либо пользователь скрыл свои матчи",
        "en": "Invalid ID or player hide matches history"
    },
    "match_history": {
        "ru": "История матчей игрока №{}\n",
        "en": "Match history of player №{}\n"
    },
    "match": {
        "ru": "Матч №{}",
        "en": "Match №{}"
    },
    "old_version": {
        "ru": "Плагин не обновлен под новый патч. Могут быть просадки в производительности или некорректное отображение новых элементов",
        "en": "Plugin is not updated for the latest patch. May be perfomance troubles and incorrect new elements displaying"
    },
    "check_assets": {
        "ru": "Проверить и скачать ассеты",
        "en": "Check and download assets"
    },
    "redownload_all": {
        "ru": "Перезагрузить все ассеты",
        "en": "Redownload all assets"
    },
    "redownload_all_warning": {
        "ru": "Данная функция полностью перезагружает все изображения. На это потребуется 5-10 минут, в зависимости от скорости вашего интернета. Продолжить?",
        "en": "This function is fully redownloading all images. This takes 5-10 minutes, depending on your Internet-connection speed. Continue?"
    },
    "check_assets_warning": {
        "ru": "Данная функция проверяет скачанные изображения и скачивает недостающие. На это потребуется 1-10 минут, в зависимости от кол-ва скачанных изображений. Продолжить?",
        "en": "This function is checking downloaded images and downloads missing. This takes 1-10 minutes, depending on downloaded count. Continue?"
    }
}

class DotaStats(BasePlugin):
    def on_plugin_load(self):
        self.heroes_dir = os.path.join(get_files_dir(), "dotastats", "heroes")
        self.items_dir = os.path.join(get_files_dir(), "dotastats", "items")
        ensure_dir_exists(self.heroes_dir)
        ensure_dir_exists(self.items_dir)
        self.data = self.load_data()
        self.add_on_send_message_hook()
        self.check_version()
        # self._load_assets()
      
    def create_settings(self):
        settings = [
            Divider(),
            Text(text=localize['check_assets']["en" if self.get_setting("lang_en", False) else "ru"], icon="media_download", on_click=self.ask_check_assets),
            Text(text=localize['redownload_all']["en" if self.get_setting("lang_en", False) else "ru"], icon="media_download", on_click=self.ask_load_assets, red=True),
            Divider(),
            Switch(key="lang_en", text="Activate for English language", default=False, icon="msg_photo_settings"),
            Divider(),
            Switch(key="alwaysimage", text=localize['always_send_images']["en" if self.get_setting("lang_en", False) else "ru"], default=False, icon="ic_gallery_background"),
            Divider(text=localize['usage']["en" if self.get_setting("lang_en", False) else "ru"])
        ]
        return settings
    
    def load_data(self):
        return requests.get("https://raw.githubusercontent.com/kingley82/dotastats_plugin/refs/heads/master/data.json").json()

    def check_version(self):
        if self.data["version"] != __version__:
            bld = AlertDialogBuilder(get_last_fragment().getParentActivity())
            bld.set_title("Dotastats")
            bld.set_message(localize['old_version']["en" if self.get_setting("lang_en", False) else "ru"])
    
    def ask_check_assets(self, view=None):
        blg = AlertDialogBuilder(get_last_fragment().getParentActivity())
        blg.set_title("Dotastats")
        blg.set_message(localize["check_assets_warning"]["en" if self.get_setting("lang_en", False) else "ru"])
        blg.set_positive_button("Yes", self._check_assets)
        blg.set_negative_button("No")
        blg.show()

    def ask_load_assets(self, view=None):
        # run_on_queue(self.load_assets, EXTERNAL_NETWORK_QUEUE)
        blg = AlertDialogBuilder(get_last_fragment().getParentActivity())
        blg.set_title("Dotastats")
        blg.set_message(localize["redownload_all_warning"]["en" if self.get_setting("lang_en", False) else "ru"])
        blg.set_positive_button("Yes", self._load_assets)
        blg.set_negative_button("No")
        blg.show()
    
    def _check_assets(self, which=None):
        run_on_queue(self.check_assets, EXTERNAL_NETWORK_QUEUE)
    
    def check_assets(self):
        ensure_dir_exists(self.heroes_dir)
        ensure_dir_exists(self.items_dir)
        max = len(self.data["HEROES_IMAGES"]) + len(self.data["ITEMS_IMAGES"]) + 1
        progress = 0
        loading_bld = AlertDialogBuilder(get_last_fragment().getParentActivity(), AlertDialogBuilder.ALERT_TYPE_LOADING)
        loading_bld.set_title("Dotastats")
        loading_bld.set_message(f"0/{max}")
        loading_bld.show()
        loading_bld.set_cancelable(False)
        having = list_dir(path=self.heroes_dir, extensions=[".png"])
        for i in self.data["HEROES_IMAGES"]:
            if not f"{i}.png" in having:
                r = requests.get(self.data["HEROES_IMAGES"][i]).content
                write_file(os.path.join(self.heroes_dir, f"{i}.png"), r)
            progress += 1
            loading_bld.set_message(f"{progress}/{max}")
            loading_bld.set_progress(int((progress/max)*100))
        having = list_dir(path=self.items_dir, extensions=[".png"])
        for i in self.data["ITEMS_IMAGES"]:
            if not f"{i}.png" in having:
                r = requests.get(self.data["ITEMS_IMAGES"][i]).content
                write_file(os.path.join(self.items_dir, f"{i}.png"), r)
            progress += 1
            loading_bld.set_message(f"{progress}/{max}")
            loading_bld.set_progress(int((progress/max)*100))
        r = requests.get("https://raw.githubusercontent.com/kingley82/dotastats_plugin/refs/heads/master/files/radiance-semibold.otf").content
        write_file(os.path.join(get_files_dir(), "dotastats", "font.otf"), r)
        loading_bld.dismiss()

    def _load_assets(self, which=None):
        run_on_queue(self.load_assets, EXTERNAL_NETWORK_QUEUE)

    def load_assets(self):
        ensure_dir_exists(self.heroes_dir)
        ensure_dir_exists(self.items_dir)
        for i in self.data["HEROES_IMAGES"]:
            r = requests.get(self.data["HEROES_IMAGES"][i]).content
            write_file(os.path.join(self.heroes_dir, f"{i}.png"), r)
        for i in self.data["ITEMS_IMAGES"]:
            r = requests.get(self.data["ITEMS_IMAGES"][i]).content
            write_file(os.path.join(self.items_dir, f"{i}.png"), r)
        r = requests.get("https://raw.githubusercontent.com/kingley82/dotastats_plugin/refs/heads/master/files/radiance-semibold.otf").content
        write_file(os.path.join(get_files_dir(), "dotastats", "font.otf"), r)
 
    def on_send_message_hook(self, account: int, params: Any) -> HookResult:
        if not isinstance(params.message, str):
            return HookResult()
        msg = params.message.strip().lower().split(" ")
        if len(msg) == 1: return
        lang = "en" if self.get_setting("lang_en", False) else "ru"
        options = 'text'
        if len(msg) >= 3:
            options = msg[2].lower()
        if params.message.startswith(".dotamatch"):
            id = msg[1]
            r = requests.get(BASE_URL+"matches/"+id).json()
            if "error" in r:
                if r["error"] == "Not Found":
                    # if lang == "ru":
                    #     params.message = f"Матч №{id} не найден"
                    # else:
                    #     params.message = f"Match №{id} not found"
                    bld = AlertDialogBuilder(get_last_fragment().getParentActivity())
                    bld.set_title("Dotastats")
                    bld.set_message(localize['match_not_found'][lang].format(id))
                    bld.show()
                return HookResult(strategy=HookStrategy.CANCEL)
            text = ""
            parsed = None
            if 'text' in options:
                # if lang == "ru":
                #     text = "Матч №" + id
                # else:
                #     text = "Match №" + id
                text = localize["match"][lang].format(id)
                text += " " + GAME_MODES[r["game_mode"]]['name'] + "\n"
                text += f"{seconds_to_normal_time(r['duration'])} - "
                # if lang == 'ru':
                #     text += f"Победа {'сил Света' if r['radiant_win'] else 'сил Тьмы'}\n\n-- Силы Света -- {'🏆' if r['radiant_win'] else ''}\n"
                # else:
                #     text += f"{'Radiant win' if r['radiant_win'] else 'Dire win'}\n\n-- Radiant -- {'🏆' if r['radiant_win'] else ''}\n"
                text += f"{localize['radiant_victory'][lang] if r['radiant_win'] else localize['dire_victory'][lang]}\n\n-- {localize['radiant'][lang]} {'🏆' if r['radiant_win'] else ''}--\n"
                players = r['players']
                for i in range(5):
                    text += "-- " + HEROES[players[i]['hero_id']] + f" [{players[i]['level']}lvl] [{players[i]['net_worth']}💰] [{players[i]['kills']}/{players[i]['deaths']}/{players[i]['assists']}]\n"
                # if lang == 'ru':
                #     text += f"\n-- Силы Тьмы -- {'🏆' if not r['radiant_win'] else ''}\n"
                # else:
                #     text += f"\n-- Dire -- {'🏆' if not r['radiant_win'] else ''}\n"
                text += f"\n -- {localize['dire'][lang]} {'🏆' if not r['radiant_win'] else ''} --\n"
                for i in range(5, 10):
                    text += "-- " + HEROES[players[i]['hero_id']] + f" [{players[i]['level']}lvl] [{players[i]['net_worth']}💰] [{players[i]['kills']}/{players[i]['deaths']}/{players[i]['assists']}]\n"
                parsed = parse_markdown(text)
            if 'image' in options:
                pass
                
            send_message({
                "peer": params.peer,
                'message': parsed.text,
                "entities": [en.to_tlrpc_object() for en in parsed.entities],
                "disable_web_page_preview": True
            })
            return HookResult(strategy=HookStrategy.CANCEL)
        elif params.message.startswith(".dotaprofile"):
            id = msg[1]
            r = requests.get(BASE_URL+"players/"+id+"/recentMatches?limit=10").json()
            # params.message = str(r)
            # return HookResult(strategy=HookStrategy.MODIFY, params=params)
            if "error" in r:
                if r["error"] == "invalid account id":
                    # if lang == "ru":
                    #     params.message = "Неверный ID, либо пользователь скрыл свои матчи"
                    # else:
                    #     params.message = "Invalid ID or player hide matches history"
                    blg = AlertDialogBuilder(get_last_fragment().getParentActivity())
                    blg.set_title("Dotastats")
                    blg.set_message(localize['invalid_id_profile'][lang])
                    blg.show()
                return HookResult(strategy=HookStrategy.CANCEL)
            if r == []:
                # if lang == "ru":
                #     params.message = "Неверный ID, либо пользователь скрыл свои матчи"
                # else:
                #     params.message = "Invalid ID or player hide matches history"
                blg = AlertDialogBuilder(get_last_fragment().getParentActivity())
                blg.set_title("Dotastats")
                blg.set_message(localize['invalid_id_profile'][lang])
                blg.show()
                return HookResult(strategy=HookStrategy.CANCEL)
            text = ""
            # if lang == "ru":
            #     text = "История матчей игрока №" + id + "\n"
            # else:
            #     text = "Match history of player №" + id + "\n"
            text = localize['match_history'][lang].format(id)
            for match in r:
                is_radiant = match["player_slot"] < 5
                win = (is_radiant and match["radiant_win"]) or (not is_radiant and not match["radiant_win"])
                text += f"{'🟩' if win else '🟥'} `{match['match_id']}` - {HEROES[match['hero_id']]} \[{match['kills']}/{match['deaths']}/{match['assists']}\]\n" 
            parsed = parse_markdown(text)
            send_message({
                "peer": params.peer,
                'message': parsed.text,
                "entities": [en.to_tlrpc_object() for en in parsed.entities]
            })
            return HookResult(strategy=HookStrategy.CANCEL)
        

