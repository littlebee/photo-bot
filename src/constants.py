import os


def env_string(name, default):
    env_val = os.getenv(name) or str(default)
    return env_val


def env_int(name, default):
    try:
        return int(env_string(name, default))
    except:
        return default


def env_float(name, default):
    try:
        return float(env_string(name, default))
    except:
        return default


def env_bool(name, default):
    value = env_string(name, default).lower()
    if value in ("true", "1"):
        return True
    else:
        return False


# Image capture dims in pixels
CAMERA_WIDTH = env_int("CAMERA_WIDTH", 2048)
CAMERA_HEIGHT = env_int("CAMERA_HEIGHT", 1536)

# which v4l channel  is the rgb image read from
CAMERA_CHANNEL = env_int("CAMERA_CHANNEL", 0)
# camera rotation if side mounted (90, 270) or upside down mounted (180)
CAMERA_ROTATION = env_int("CAMERA_ROTATION", 0)
CAMERA_AUTO_EXPOSURE = env_float("CAMERA_AUTO_EXPOSURE", 0.75)


LOG_ALL_MESSAGES = env_bool("LOG_ALL_MESSAGES", False)

# vision http server
SERVER_PORT = env_int("SERVER_PORT", 5000)

TWERK_PHOTO_UPLOAD_URL = env_string(
    "TWERK_PHOTO_UPLOAD_URL", "http://athena.local:3000/api/photoUpload"
)
