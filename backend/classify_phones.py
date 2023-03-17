def classify_battery_life(battery_data):
    capacity__mAh = battery_data.get("capacity__mAh", 0)
    audio = battery_data.get("continuous_audio_playtime__h", 0)
    video = battery_data.get("continuous_video_playtime__h", 0)

    """ Capacity message """
    if (capacity__mAh == 0):
        capacity_message = ""
    elif (0 < capacity__mAh <= 50):
        capacity__mAh = "You have a low storage capacity"
    elif (50 < capacity__mAh <= 100):
        capacity_message = "You have an average storage capacity"
    else:
        capacity_message = "You have a high storage capacity"

    """ Audio playtime message """
    if (audio == 0):
        audio_message = ""
    elif (0 < audio <= 5):
        audio_message = f"{audio} hours is a low audio playtime"
    elif (5 < audio <= 10):
        audio_message = f"{audio} hours is an average audio playtime"
    else:
        audio_message = f"{audio} hours is a high audio playtime"

    """ Video playtime message """
    if (video == 0):
        video_message = ""
    elif (0 < video <= 3):
        vidio_message = f"{video} hours is a low vidio playtime"
    elif (3 < video <= 6):
        vidio_message = f"{video} hours is an average vidio playtime"
    else:
        vidio_message = f"{video} hours is a high vidio playtime"

    """ Classification """
    classification = (
        f"{capacity_message} {audio_message} {vidio_message}"
    )

    return classification

def classify_screen_size(screen_data):
    screen_size_inches = screen_data.get("screen_size_inches", 0)
    if screen_size_inches == 0:
        screen_size_message = ""
    elif screen_size_inches <= 4:
        screen_size_message = "You have a small screen size"
    elif 4 < screen_size_inches <= 6:
        screen_size_message = "You have an average screen size"
    else:
        screen_size_message = "You have a large screen size"
    return screen_size_message

def classify_camera_quality(camera_data):
    rear_camera_resolution_MPs = camera_data.get("rear_camera_resolution_MPs", 0)
    front_camera_resolution_MPs = camera_data.get("front_camera_resolution_MPs", 0)
    megapixels = camera_data.get("megapixels", 0)

    if (rear_camera_resolution_MPs == 0) and (front_camera_resolution_MPs == 0):
        camera_message = ""
    elif rear_camera_resolution_MPs > front_camera_resolution_MPs:
        camera_message = "You have a better rear camera"
    elif front_camera_resolution_MPs > rear_camera_resolution_MPs:
        camera_message = "You have a better front camera"
    else:
        camera_message = "You have the same resolution for both cameras"

    if megapixels == 0:
        message = "This device doesn't have a camera."
    elif megapixels <= 5:
        message = "The camera on this device has a low resolution."
    elif megapixels <= 12:
        message = "The camera on this device has an average resolution."
    else:
        message = "The camera on this device has a high resolution."

    return message

    return camera_message

def classify_price(price_data):
    price_USD = price_data.get("price_USD", 0)

    if price_USD == 0:
        price_message = ""
    elif price_USD <= 200:
        price_message = "You have a budget phone"
    elif 200 < price_USD <= 700:
        price_message = "You have a mid-range phone"
    else:
        price_message = "You have a premium phone"

    return price_message


if __name__ == "__main__":
    import json

    with open("phones_raw.json", "r") as db:
        data = json.load(db)

    for phone in data:
        if 