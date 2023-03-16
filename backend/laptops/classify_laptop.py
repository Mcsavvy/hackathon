"""
Classify Laptop Data.

This file contains functions that take in a laptop's data and is able to
produce detailed classifications using the data. The classifications sound
naturals as if coming from a sales person.

"""


from cohere import Client
import os
import threading
from ..config import DATABASE, COHERE_API_KEY
from cohere.client import ClassifyExample
import json
from pathlib import Path

cohere = Client(COHERE_API_KEY)


def classify_laptop_audio(audio_data) -> str:
    """
    Classify laptop audio data.

    Args:
        audio_data: the data to classify
    Returns:
        The classification
    """
    has_speakers = audio_data.get("has_speakers", False)
    has_headphone_jack = audio_data.get("has_headphone_jack", False)
    has_microphone = audio_data.get("has_microphone", False)
    num_speakers = audio_data.get("number_of_speakers", 1)
    if num_speakers == 0:
        speakers_message = ""
    elif num_speakers == 1:
        speakers_message = "Has a single built-in speaker."
    else:
        speakers_message = f"Has {num_speakers} built-in speakers."
    num_headphone_outputs = audio_data.get("number_of_headphone_outputs", 0)
    if num_headphone_outputs == 0:
        headphone_message = ""
    elif num_headphone_outputs == 1:
        headphone_message = "Has a single headphone jack."
    else:
        headphone_message = f"Has {num_headphone_outputs} headphone jacks."
    num_microphones = audio_data.get("number_of_microphones", 0)
    if num_microphones == 0:
        mic_message = ""
    elif num_microphones == 1:
        mic_message = "Has a single built-in microphone."
    else:
        mic_message = f"Has {num_microphones} built-in microphones."
    audio_chip_brand = audio_data.get("audiochip", "")
    determiner = "a"
    if audio_chip_brand:
        if audio_chip_brand.startswith(tuple("aeiou")):
            determiner = "an"
        audio_chip_message = (
            f"This laptop uses {determiner} {audio_chip_brand} audio chip for"
            " audio."
        )
    else:
        audio_chip_message = ""
    # Combine all the messages to form the final classification
    classification = (
        f"{speakers_message} {headphone_message}"
        f" {mic_message} {audio_chip_message}".strip()
    )
    # Return the classification
    return classification


def classify_laptop_battery(battery_data) -> str:
    """
    Classify laptop battery data.

    Args:
        battery_data: the data to classify
    Returns:
        The classification
    """
    capacity = battery_data.get("capacity__wh", 0)
    technology = battery_data.get("technology", "unspecified")
    battery_life = battery_data.get("battery_life__h", 0)
    charging_time = battery_data.get("charging_time__h", 0)

    if capacity == 0:
        capacity_message = ""
    elif capacity < 50:
        capacity_message = "Has a small battery capacity."
    elif capacity < 100:
        capacity_message = "Has an average battery capacity."
    else:
        capacity_message = "Has a large battery capacity."

    if technology == "unspecified":
        technology_message = ""
    else:
        technology_message = f"the battery uses {technology} technology."

    if battery_life == 0:
        battery_life_message = ""
    elif battery_life < 5:
        battery_life_message = "the battery has a short life."
    elif battery_life < 10:
        battery_life_message = "the battery has an average life."
    else:
        battery_life_message = "the battery has a long life."

    if charging_time == 0:
        charging_time_message = ""
    elif charging_time < 2:
        charging_time_message = "the battery charges quickly."
    elif charging_time < 4:
        charging_time_message = "the battery has an average charging time."
    else:
        charging_time_message = "the battery takes a long time to charge."

    classification = (
        f"{capacity_message} {technology_message} "
        f"{battery_life_message} {charging_time_message} "
    )
    return classification


def classify_laptop_camera(camera_data) -> str:
    """
    Classify laptop camera data.

    Args:
        camera_data: the data to classify
    Returns:
        The classification
    """
    has_front_camera = camera_data.get("has_camera_front", False)
    has_back_camera = camera_data.get("has_camera_back", False)
    camera_type = camera_data.get("type", "unspecified")
    camera_privacy_type = camera_data.get("type_privacy", "unspecified")
    front_camera_megapixel = camera_data.get("camera_front__mp", 0)
    front_camera_resolution = camera_data.get("camera_front_resolution__p", 0)
    capturing_speed = camera_data.get("capturing_speed__fps", 0)
    has_infrared = camera_data.get("has_infrared", False)
    has_privacy_camera = camera_data.get("has_privacy_camera", False)

    messages = []
    if has_front_camera:
        if front_camera_megapixel and front_camera_resolution:
            messages.append(
                "Has front camera with "
                f"{front_camera_megapixel}MP and {front_camera_resolution}p"
                " resolution."
            )
        elif front_camera_megapixel:
            messages.append(
                "Has front camera with " f"{front_camera_megapixel}MP quality."
            )
        elif front_camera_resolution:
            messages.append(
                "Has front camera with "
                f"{front_camera_resolution}p resolution."
            )
        else:
            messages.append("Has front camera.")
    if has_back_camera:
        messages.append("Has a back camera.")
    if capturing_speed > 0:
        messages.append(f"The camera can capture at {capturing_speed} FPS.")
    if has_infrared:
        messages.append("Has an infrared camera.")
    if has_privacy_camera:
        messages.append(
            ("Has a privacy camera with" f"{camera_privacy_type} technology.")
        )
    classification = " ".join(x for x in messages if x)
    return classification


def classify_laptop_cpu(cpu_data) -> str:
    """
    Classify laptop CPU data.

    Args:
        cpu_data: the data to classify
    Returns:
        The classification
    """
    generation = cpu_data.get("generation", "unspecified")
    number_of_cores = cpu_data.get("number_of_cores", 0)
    clock_speed = cpu_data.get("clock_speed__ghz", 0)
    max_clock_speed = cpu_data.get("max_clock_speed__ghz", 0)

    if generation == "unspecified":
        generation_message = ""
    else:
        generation_message = f"generation {generation}"

    if number_of_cores == 0:
        number_of_cores_message = ""
    elif number_of_cores < 4:
        number_of_cores_message = "with a few cores"
    elif number_of_cores < 8:
        number_of_cores_message = "with several cores"
    else:
        number_of_cores_message = "with many cores"

    if clock_speed == 0:
        clock_speed_message = ""
    else:
        clock_speed_message = f"at {clock_speed} GHz"

    if max_clock_speed == 0:
        max_clock_speed_message = ""
    elif max_clock_speed < 3:
        max_clock_speed_message = "with low turbo boost"
    elif max_clock_speed < 4:
        max_clock_speed_message = "with average turbo boost"
    else:
        max_clock_speed_message = "with high turbo boost"

    classification = (
        f"This laptop has a {generation_message} CPU {number_of_cores_message}"
        f" {clock_speed_message} {max_clock_speed_message}."
    )
    return classification


def classify_laptop_design(design_data) -> str:
    """
    Classify laptop design data.

    Args:
        design_data: the data to classify
    Returns:
        The classification
    """
    color = design_data.get("color", "")
    color_name = design_data.get("color_name", "")
    material = design_data.get("material", "unspecified")

    color_message = (
        f"The laptop's color is {color_name or color}."
        if color or color_name != "unspecified"
        else ""
    )
    material_message = (
        f"The laptop is made of {material}."
        if material != "unspecified"
        else ""
    )

    classification = f"{color_message} {material_message}".strip()
    return classification


def classify_laptop_display(display_data) -> str:
    """
    Classify laptop display data.

    Args:
        display_data: the data to classify
    Returns:
        The classification
    """
    max_brightness = display_data.get("brightness__cdm", 0)
    has_anti_reflection = display_data.get("has_anti_reflection", False)
    has_dual_screen = display_data.get("has_dual_screen", False)
    has_touchscreen = display_data.get("has_touchscreen", False)
    hd_type = display_data.get("hd_type", "")
    max_refresh_rate = display_data.get("max_refresh_rate__hz", 0)
    pixel_density = display_data.get("pixel_density__ppi", 0)
    size = display_data.get("size__inch", 0)
    technology = display_data.get("technology", "")
    messages = []

    if max_brightness == 0:
        pass
    elif max_brightness < 300:
        messages.append("Dim display")
    elif max_brightness < 500:
        messages.append("Bright display")
    else:
        messages.append("Very bright display")

    if has_anti_reflection:
        messages.append("with anti-reflection technology")

    if has_dual_screen:
        messages.append("with dual screen")

    if has_touchscreen:
        messages.append("with touchscreen")

    if hd_type == "OLED":
        messages.append("with OLED display")
    elif hd_type == "IPS":
        messages.append("with IPS display")
    elif hd_type == "VA":
        messages.append("with VA display")
    elif hd_type == "TN":
        messages.append("with TN display")

    if max_refresh_rate == 0:
        pass
    elif max_refresh_rate < 60:
        messages.append("with low refresh rate")
    elif max_refresh_rate < 120:
        messages.append("with high refresh rate")
    else:
        messages.append("with very high refresh rate")

    if pixel_density == 0:
        pass
    elif pixel_density < 200:
        messages.append("with low pixel density")
    elif pixel_density < 300:
        messages.append("with moderate pixel density")
    else:
        messages.append("with high pixel density")

    if size == 0:
        pass
    elif size < 13:
        messages.append("with a small display")
    elif size < 16:
        messages.append("with a medium-sized display")
    else:
        messages.append("with a large display")

    if technology == "LED":
        messages.append("with LED backlight")
    elif technology == "OLED":
        messages.append("with OLED technology")

    if messages:
        return "This laptop has a display {}".format(" ".join(messages))
    return ""


def classify_laptop_keyboard(keyboard_data) -> str:
    """
    Classify laptop keyboard data.

    Args:
        keyboard_data: the data to classify
    Returns:
        The classification
    """
    keyboard_type = keyboard_data.get("type", "unspecified")
    has_light = keyboard_data.get("has_light", False)
    color_light = keyboard_data.get("color_light", "unspecified")
    has_numeric_keyboard = keyboard_data.get("has_numeric_keyboard", False)
    has_programmable_keys = keyboard_data.get("has_programmable_keys", False)
    has_touchbar = keyboard_data.get("has_touchbar", False)
    has_touchpad = keyboard_data.get("has_touchpad", False)
    type_touchpad = keyboard_data.get("type_touchpad", "unspecified")

    if keyboard_type == "unspecified":
        keyboard_type_message = ""
    else:
        keyboard_type_message = f"a {keyboard_type} keyboard"

    if has_light:
        if color_light == "unspecified":
            color_light_message = "with backlight"
        else:
            color_light_message = f"with {color_light} backlight"
    else:
        color_light_message = ""

    if has_numeric_keyboard:
        numeric_keyboard_message = "with numeric keypad"
    else:
        numeric_keyboard_message = ""

    if has_programmable_keys:
        programmable_keys_message = "with programmable keys"
    else:
        programmable_keys_message = ""

    if has_touchbar:
        touchbar_message = "with Touch Bar"
    else:
        touchbar_message = ""

    if has_touchpad:
        if type_touchpad == "unspecified":
            touchpad_message = "with touchpad"
        else:
            touchpad_message = f"with {type_touchpad} touchpad"
    else:
        touchpad_message = ""

    classification = "This laptop has {}.".format(
        " ".join(
            x
            for x in (
                keyboard_type_message,
                color_light_message,
                programmable_keys_message,
                touchpad_message,
            )
            if x
        )
    )
    return classification


def classify_laptop_measurements(measurements_data) -> str:
    """
    Classify laptop measurements.

    Args:
        measurements_data: the data to classify
    Returns:
        The classification
    """
    height = measurements_data.get("height__mm", 0)
    height_back = measurements_data.get("height_back__mm", 0)
    height_front = measurements_data.get("height_front__mm", 0)
    length = measurements_data.get("length__mm", 0)
    weight = measurements_data.get("weight__g", 0)
    width = measurements_data.get("width__mm", 0)

    # classify based on height, length, width, and weight
    if height_front < 10 and height_back < 15:
        height_classification = "thin"
    elif height_front < 15 and height_back < 20:
        height_classification = "slim"
    else:
        height_classification = "thick"

    if length < 300:
        length_classification = "short"
    elif length < 350:
        length_classification = "medium"
    else:
        length_classification = "long"

    if width < 200:
        width_classification = "narrow"
    elif width < 250:
        width_classification = "medium"
    else:
        width_classification = "wide"

    if weight < 1000:
        weight_classification = "light"
    elif weight < 2000:
        weight_classification = "medium"
    else:
        weight_classification = "heavy"

    # combine classifications into final string
    classification = (
        f"This laptop is {height_classification} and {length_classification} "
        f"with a {width_classification} design, "
        f"and it's {weight_classification}."
    )
    return classification


def classify_laptop_memory(memory_data) -> str:
    """
    Classify laptop memory data.

    Args:
        memory_data: the data to classify
    Returns:
        The classification
    """
    memory_type = memory_data.get("type", "unspecified")
    max_ram = memory_data.get("max_ram__gb", 0)
    ram = memory_data.get("ram__gb", 0)
    is_memory_expandable = memory_data.get("is_memory_expandable", False)
    number_of_slots = memory_data.get("number_of_slots", 0)
    layout = memory_data.get("layout__gb", 0)
    cache_memory = memory_data.get("cache_memory__mb", 0)
    clock_speed = memory_data.get("clock_speed__ghz", 0)
    form_factor = memory_data.get("form_factor", "unspecified")
    slots = memory_data.get("slots", "unspecified")

    message_parts = []
    if memory_type != "unspecified":
        message_parts.append(f"{memory_type} memory")
    if max_ram > 0:
        message_parts.append(f"upgradable to {max_ram}GB")
    if ram > 0:
        message_parts.append(f"{ram}GB installed")
    if is_memory_expandable:
        message_parts.append("expandable memory")
    if number_of_slots > 0:
        message_parts.append(f"{number_of_slots} memory slots")
    if str(layout) != "0":
        message_parts.append(f"{layout} memory layout")
    if cache_memory > 0:
        message_parts.append(f"{cache_memory}MB cache memory")
    if clock_speed > 0:
        message_parts.append(f"{clock_speed}GHz clock speed")
    if form_factor != "unspecified":
        message_parts.append(f"{form_factor} form factor")
    if slots != "unspecified":
        message_parts.append(f"{slots} slots")

    if len(message_parts) == 0:
        classification = ""
    else:
        classification = f"This laptop has {' and '.join(message_parts)}."
    return classification


def classify_laptop_network(network_data) -> str:
    """
    Classify laptop network data.

    Args:
        network_data: the data to classify
    Returns:
        The classification
    """
    has_bluetooth = network_data.get("has_bluetooth", False)
    has_ethernet_lan = network_data.get("has_ethernet_lan", False)
    has_mobile_connection = network_data.get("has_mobile_connection", False)
    max_wireless_data_transfer_rate = network_data.get(
        "max_wireless_data_transfer_rate__mbits", 0
    )
    manufacturer_wlan_controller = network_data.get(
        "manufacturer_wlan_controller", "unknown"
    )
    type_antenna = network_data.get("type_antenna", "unknown")
    type_wlan_controller = network_data.get("type_wlan_controller", "unknown")
    wifi_standards = network_data.get("wifi_standards", "unknown")

    classification = o = "This laptop has the following features: "
    if has_bluetooth:
        classification += "Bluetooth, "
    if has_ethernet_lan:
        classification += "Ethernet LAN, "
    if has_mobile_connection:
        classification += "Mobile data, "
    if max_wireless_data_transfer_rate > 0:
        classification += (
            "a maximum wireless data transfer rate of "
            f"{max_wireless_data_transfer_rate} Mbps, "
        )
    if manufacturer_wlan_controller != "unknown":
        classification += (
            "a WLAN controller manufactured by "
            f"{manufacturer_wlan_controller}, "
        )
    if type_antenna != "unknown":
        classification += f"a {type_antenna} antenna, "
    if type_wlan_controller != "unknown":
        classification += f"a {type_wlan_controller} WLAN controller, "
    if wifi_standards != "unknown":
        classification += f"supports {wifi_standards}."
    if classification == o:
        classification = ""
    return classification


def classify_laptop_ports_interface(ports_data) -> str:
    """
    Classify laptop ports and interfaces.

    Args:
        ports_data: the data to classify
    Returns:
        The classification
    """
    port_types = []
    if ports_data.get("has_usb_a_gen_1", False):
        port_types.append("USB-A Gen 1")
    if ports_data.get("has_usb_a_gen_2", False):
        port_types.append("USB-A Gen 2")
    if ports_data.get("has_usb_c_gen_2", False):
        port_types.append("USB-C Gen 2")
    if ports_data.get("has_usb_c_displayport_alternative_modus", False):
        port_types.append("USB-C DisplayPort alternative mode")
    if ports_data.get("has_usb_power_delivery", False):
        port_types.append("USB Power Delivery")
    if ports_data.get("has_thunderbolt", False):
        port_types.append("Thunderbolt")
    if ports_data.get("has_mini_displayport", False):
        port_types.append("Mini DisplayPort")
    if ports_data.get("has_displayport", False):
        port_types.append("DisplayPort")
    if ports_data.get("has_dvi_poort", False):
        port_types.append("DVI")
    if ports_data.get("has_vga_port", False):
        port_types.append("VGA")

    if not port_types:
        return ""
    elif len(port_types) == 1:
        return "This laptop has a {} port.".format(port_types[0])
    else:
        port_list = ", ".join(port_types[:-1]) + " and " + port_types[-1]
        return "This laptop has {} ports.".format(port_list)


def classify_laptop_security(security_data) -> str:
    """
    Classify laptop security features.

    Args:
        security_data: the data to classify
    Returns:
        The classification
    """
    has_fingerprint_reader = security_data.get("has_fingerprint_reader")
    has_option_for_cable_lock = security_data.get("has_option_for_cable_lock")
    has_password_protection = security_data.get("has_password_protection")
    has_smart_card_reader = security_data.get("has_smart_card_reader")

    messages = []

    if has_fingerprint_reader:
        messages.append("a fingerprint reader")
    if has_option_for_cable_lock:
        messages.append("cable lock")
    if has_password_protection:
        messages.append("password protection")
    if has_smart_card_reader:
        messages.append("a smart card reader")

    if len(messages) == 0:
        return "This laptop does not have any security features."
    else:
        return "This laptop has {}.".format(", ".join(messages))


def classify_laptop_software(software_data) -> str:
    """
    Classify laptop software data.

    Args:
        software_data: the data to classify
    Returns:
        The classification
    """
    os = software_data.get("os", "unspecified")
    os_architecture = software_data.get("os_architecture__bit", "unspecified")
    os_language = software_data.get("os_language", "unspecified")
    available_software = software_data.get("available_software", "unspecified")
    trialsoftware = software_data.get("trialsoftware", "unspecified")

    messages = []

    if os != "unspecified":
        messages.append(f"running {os} {os_architecture}-bit")
        if os_language != "unspecified":
            messages.append(f"with {os_language} language pack")

    if available_software != "unspecified":
        messages.append(f"with {available_software} software pre-installed")

    if trialsoftware != "unspecified":
        messages.append(f"with {trialsoftware} trial software pre-installed")

    if not messages:
        messages.append("with unspecified software")

    return "This laptop comes {}.".format(" ".join(messages))


def classify_laptop_storage(storage_data) -> str:
    """
    Classify laptop storage data.

    Args:
        storage_data: the data to classify
    Returns:
        The classification
    """
    messages = []

    # Check storage type and capacity
    storage_type = storage_data.get("type")
    storage_capacity = storage_data.get("capacity__gb")
    if storage_type and storage_capacity:
        messages.append(f"with a {storage_capacity} GB {storage_type} drive")

    # Check if storage is expandable
    is_expandable = storage_data.get("is_storage_expandable", False)
    if is_expandable:
        messages.append("with expandable storage")

    # Check if storage has NVMe and hard drive accelerator
    has_nvme = storage_data.get("has_nvme", False)
    has_hda = storage_data.get("hard_drive_accelerator", False)
    if has_nvme:
        messages.append("with NVMe storage technology")
    if has_hda:
        messages.append("with hard drive accelerator")

    # Check if storage has an integrated memory
    # card reader and compatible memory cards
    has_card_reader = storage_data.get("has_integrated_memory_card_reader")
    compatible_cards = storage_data.get("compatible_memory_cards")
    if has_card_reader:
        messages.append("with an integrated memory card reader")
        if compatible_cards:
            messages.append(f"that supports {compatible_cards} memory cards")

    # Check if storage has SSDs and their capacity and interfaces
    num_ssds = storage_data.get("number_of_ssd", 0)
    if num_ssds > 0:
        ssd_capacity = storage_data.get("ssd_capacity__gb", "unspecified")
        ssd_interfaces = storage_data.get("ssd_interfaces", "unspecified")
        if ssd_capacity != "unspecified" and ssd_interfaces != "unspecified":
            messages.append(
                (
                    f"with {num_ssds} SSD(s) ({ssd_capacity} GB, "
                    f"{ssd_interfaces} interfaces)"
                )
            )
    if not messages:
        return ""
    return "This laptop comes {}.".format(" ".join(messages))


def classify_laptop_video(video) -> str:
    """
    Classify laptop video data.

    Args:
        video: the data to classify
    Returns:
        The classification
    """
    messages = []

    if video.get("has_4k_support", False):
        messages.append("with 4K video support")

    if video.get("has_6k_support", False):
        messages.append("with 6K video support")

    if video.get("has_cuda", False):
        messages.append("with NVIDIA CUDA technology")

    has_video_card = False

    if video.get("has_internal_video_card"):
        int_type = video.get("internal_video_card_type")
        if int_type:
            messages.append(f"with internal {int_type} video card")
        else:
            messages.append("with internal video card")
        has_video_card = True

    if video.get("has_separate_video_card", False):
        sep_type = video.get("separate_video_card_type")
        if sep_type:
            messages.append(f"with separate {sep_type} video card")
        has_video_card = True

    if has_video_card:
        memory_gb = video.get("memory__gb", 0)
        if memory_gb > 0:
            messages.append(f"with {memory_gb}GB video memory")
            memory_type = video.get("memory_type")
            if memory_type:
                messages.append(f"with {memory_type} video memory type")
            max_memory_bandwidth_gbs = video.get("max_memory_bandwidth__gbs")
            if max_memory_bandwidth_gbs:
                messages.append(
                    (
                        "with max memory bandwidth of "
                        f"{max_memory_bandwidth_gbs}GB/s"
                    )
                )

    if video.get("has_nvidia_max_q", False):
        messages.append("with NVIDIA Max-Q technology")

    if video.get("manufacturer", False):
        messages.append(f"manufactured by {video['manufacturer']}")

    if not messages:
        return ""

    return "This laptop comes {}.".format(" ".join(messages))


def classify_based_on_specs(data: list[dict], status= None) -> list[list[str]]:
    """
    Classify laptop based on it's specs.

    Laptops can be classified based on the following specs:

    - audio
    - battery
    - cpu
    - camera
    - design
    - display
    - keyboard
    - memory
    - storage
    - video
    - software
    - ports

    Args:
        data: A list of dictionaries, each representing a laptop
    Returns:
        a list of classifications for each laptop
    """
    classifications: list[list[str]] = []
    specs: tuple[str, ...] = (
        "audio", "camera", "video", "design", "memory",
        "battery", "display", "network", "storage",
        "keyboard", "security", "software", "measurements",
        "ports_interface", "cpu"
    )
    for laptop in data:
        classifications.append([])
        classification: list[str] = classifications[-1]
        if not (laptop_data := laptop["data"]):
            continue
        for spec in specs:
            handler = globals()[f"classify_laptop_{spec}"]
            details = laptop_data.get(spec, '')
            if not details:
                classification.append('')
                continue
            classification.append(handler(details))
    return classifications


def classify_based_on_group(data: list[dict], status=None) -> list[list[str]]:
    """
    Classify laptops based on users.

    Laptops can be further classified based on the group
    of users that the laptop was aimed at, these groups are:

    - Everyday users
    - Students
    - Business professionals
    - Creative professionals
    - Gamers
    - Hardcore users

    Args:
        data: A list of dictionaries, each representing a laptop
    Returns:
        a list of classifications for each laptop
    """
    
    examples = []
    inputs = []
    classifications: list[list[str]] = []

    def classify(batch: list[str]):
        # Classify the inputs using the Cohere API
        response = client.classify(inputs=batch, examples=examples, model="large")
    
        status.update("Processing classifications...")
        # Extract the classification labels and confidences for each input
        for classification in response.classifications:
            labels = []
            predictions: list[tuple[str, float]] = []
            for label, pred in classification.labels.items():
                # Append the (label, confidence) tuple to the predictions list
                predictions.append((label, pred.confidence))
            # Sort the predictions list in ascending order of confidence
            predictions.sort(key=lambda p: p[1])
            # Only keep the labels with a confidence greater than 5
            for pred in predictions:
                if pred[1] > 5:
                    labels.append(pred[0])
            # If no labels meet the confidence threshold, use the predicted label
            if not labels:
                labels.append(classification.prediction)
            # Append the labels to the classifications list
            classifications.append(labels)

    # Load the examples from a json file located in the same directory as this script
    examples_file = Path(__file__).parent.joinpath("users_examples.json")
    for ex in json.loads(examples_file.read_text()):
        # Create an Example object from each example in the file and append it to the examples list
        examples.append(Example(ex[0], ex[1]))
    
    status.update("Fetching data...")
    # Extract the input texts from the input dictionaries
    batch = []
    batch_count = 1
    for laptop in data:
        if len(batch) >= 96:
            status.update(f"Classifying batch {batch_count}...")
            classify(batch)
            batch = []
            batch_count += 1
        batch.append(laptop["info"] or laptop["name"])
    if len(batch) >= 1:
        status.update(f"Classifying batch {batch_count}...")
        classify(batch)
        batch = []
        batch_count += 1
        
    
    return classifications


def classify_laptop(laptop: dict):
    yield f"This laptops's name is {laptop['name']}."
    yield f"This laptops model is {laptop['mpn']}"
    if laptop["info"]:
        yield laptop["info"]
    yield laptop["spec_info"]
    yield f"This laptop would be a good fit for {laptop['target_user']}."


def generate_description():
    """
    Generate description for laptop.

    Args:
        data: the data to use to generate the description
    """
    from ..config import LAPTOP_DB
    from rich import get_console
    import time


    console = get_console()


    data = json.loads(LAPTOP_DB.read_text())
    count = 0
    with console.status("blah...") as status:
        for laptop in data:
            if laptop.get("description"):
                continue
            if count >= 5:
                console.log("sleeping 💤💤")
                time.sleep(60)
                console.log("waking up!")
                count = 0
            status.update(f"Classifying laptop {laptop['id']}. ")
            desc = classify_laptop(laptop)
            description_raw = " ".join(
                c.strip() for c in desc)
            response = cohere.summarize(
                text=description_raw,
                model="summarize-medium",
                temperature=0.5,
                extractiveness="high",
                length="long"
            )
            laptop["description"] = response.summary
            LAPTOP_DB.write_text(json.dumps(data))
            console.log(f"Finished laptop {laptop['id']} ✔")
            count += 1
