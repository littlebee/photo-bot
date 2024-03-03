import requests
import constants as c

import log


def rotate_360():
    url = c.ROTOBOT_API_URL + "rotate_360"
    log.info(f"rotobot_api: invoking {url}")
    response = requests.get(url)
    log.info(f"rotobot_api: resp from {url}: {response.json()}")
