import os
from typing import Dict, List

from utils import Tools
from config import KANDA_IDS, RAMAYANA_VERSIONS, Verses

read_json = Tools.read_json
logger = Tools.setup_logger("query_ramayana")
safe_run = Tools.safe_run

class DataProcessing:
    def __init__(self):
        """
        """
        self.valmiki_data = self.load_valmiki_verses()
        self.tulsidas_data = self.load_tulsidas_verses()

    def _decode_key(self, encoded: str, ramayana_version: RAMAYANA_VERSIONS) -> tuple[str, str]:
        kanda_id, rest = encoded.split('.', 1)

        kanda_dict = KANDA_IDS[ramayana_version]
        reversed_kanda = {v: k for k, v in kanda_dict.items()}

        if int(kanda_id) not in reversed_kanda:
            raise ValueError(f"Unknown kanda ID: {int(kanda_id)}")

        kanda_name = reversed_kanda[int(kanda_id)]
        key = rest.replace('.', '_')
        return key, kanda_name

    def load_valmiki_verses(self) -> Dict[str, list[Verses]]:
        """
        Load Valmiki verses from the JSON file.
        """
        valmiki_folder = 'dataset/Valmiki'
        valmiki_data = {key: [] for key in KANDA_IDS[RAMAYANA_VERSIONS.VALMIKI]}
        for f in os.listdir(valmiki_folder):
            if f.endswith('.json'):
                filepath = os.path.join(valmiki_folder, f)
                kanda = read_json(filepath)
                for item in kanda:
                    for key, value in item.items():
                        valmiki_data[f.replace('.json','')].append(
                            Verses(
                                _id = key,
                                verse = value['shloka']
                            )
                        )

        return valmiki_data

    def load_tulsidas_verses(self) -> list[Verses]:
        """
        Load Tulsidas verses from the JSON files.
        """
        tulsidas_folder = 'dataset/Tulsidas'
        tulsidas_data = {key: [] for key in KANDA_IDS[RAMAYANA_VERSIONS.TULSIDAS]}
        for f in os.listdir(tulsidas_folder):
            if f.endswith('.json'):
                filepath = os.path.join(tulsidas_folder, f)
                kanda = read_json(filepath)
                for sarga in kanda:
                    for content in sarga:
                        tulsidas_data[f.replace('.json','')].append(
                            Verses(
                                _id = content["_id"],
                                verse = content['verse']
                            )
                        )

        return tulsidas_data
    
    def retrive_verse(self, _id, ramayana_version: RAMAYANA_VERSIONS) -> str:
        """
        Retrieve a verse based on the ramayana version.
        """
        if ramayana_version == RAMAYANA_VERSIONS.VALMIKI:
            verses = self.valmiki_data
            
        elif ramayana_version == RAMAYANA_VERSIONS.TULSIDAS:
            verses = self.tulsidas_data

        id, kanda_name = self._decode_key(_id, ramayana_version)

        return next((v.verse for v in verses[kanda_name] if v._id == id), "")

