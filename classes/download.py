import platform
import hashlib
import os
import shutil
import inspect

import requests
from tqdm import tqdm


class HashError(Exception):
    pass


stack = inspect.stack()
for s in stack[1:]:
    m = inspect.getmodule(s[0])
    if m:
        file_path = m.__file__
        break


def download_jdk():
    os.mkdir(os.path.join(os.path.dirname(file_path), "assets/java"))
    system = platform.system()
    java_url = {
        "Darwin": "https://aka.ms/download-jdk/microsoft-jdk-16.0.2.7.1-macOS-aarch64.tar.gz",  # Microsoft JDK (ARM)
        "Linux": "https://download.java.net/java/GA/jdk16.0.2/d4a915d82b4c4fbb9bde534da945d746/7/GPL/openjdk-16.0.2_linux-x64_bin.tar.gz",  # OpenJDK (x64)
        "Windows": "https://download.java.net/java/GA/jdk16.0.2/d4a915d82b4c4fbb9bde534da945d746/7/GPL/openjdk-16.0.2_windows-x64_bin.zip",  # OpenJDK (x64)
        "hash_Darwin": "https://aka.ms/download-jdk/microsoft-jdk-16.0.2.7.1-macOS-aarch64.tar.gz.sha256sum.txt",  #  microsoft-jdk-16.0.2.7.1-macOS-aarch64.tar.gzを取り除く(メモ)
        "hash_Linux": "https://download.java.net/java/GA/jdk16.0.2/d4a915d82b4c4fbb9bde534da945d746/7/GPL/openjdk-16.0.2_linux-x64_bin.tar.gz.sha256",
        "hash_Windows": "https://download.java.net/java/GA/jdk16.0.2/d4a915d82b4c4fbb9bde534da945d746/7/GPL/openjdk-16.0.2_windows-x64_bin.zip.sha256",
    }
    fs = int(requests.head(java_url[system]).headers["content-length"])
    res = requests.get(java_url[system], stream=True)
    progress = tqdm(total=fs, unit="B", unit_scale=True)
    with open(
        os.path.join(
            os.path.dirname(file_path),
            "assets/java/{}".format(
                java_url[system][java_url[system].rfind("/") + 1 :]
            ),
        ),
        "wb",
    ) as f:
        for chunk in res.iter_content(chunk_size=1024):
            f.write(chunk)
            progress.update(len(chunk))
        progress.close()

    if system == "Darwin":
        hash_w = requests.get(java_url["hash_" + system]).text.replace(
            "  microsoft-jdk-16.0.2.7.1-macOS-aarch64.tar.gz", ""
        )
    else:
        hash_w = requests.get(java_url["hash_" + system]).text
    with open(
        os.path.join(
            os.path.dirname(file_path),
            "assets/java/{}".format(
                java_url[system][java_url[system].rfind("/") + 1 :]
            ),
        ),
        "rb",
    ) as hashFile:
        hash_sha256 = hashlib.sha256(hashFile.read()).hexdigest()
        if hash_sha256 == hash_w:
            pass
        else:
            raise HashError(
                "Hash value does not match.\n\nFile: {}\nRemote: {}".format(
                    hash_sha256, hash_w
                )
            )
    shutil.unpack_archive(
        os.path.join(
            os.path.dirname(file_path),
            "assets/java/{}".format(
                java_url[system][java_url[system].rfind("/") + 1 :]
            ),
        ),
        extract_dir=os.path.join(os.path.dirname(file_path), "assets/java"),
    )
    if system == "Darwin":
        os.rename(
            os.path.join(
                os.path.dirname(file_path), "assets/java/jdk-16.0.2+7/Contents/Home"
            ),
            os.path.join(os.path.dirname(file_path), "assets/java/jdk-16.0.2"),
        )
    os.remove(
        os.path.join(
            os.path.dirname(file_path),
            "assets/java/{}".format(
                java_url[system][java_url[system].rfind("/") + 1 :]
            ),
        )
    )


def download_sjar():
    sj_url = "https://launcher.mojang.com/v1/objects/bb2b6b1aefcd70dfd1892149ac3a215f6c636b07/server.jar"
    fs = int(requests.head(sj_url).headers["content-length"])
    res = requests.get(sj_url, stream=True)
    progress = tqdm(total=fs, unit="B", unit_scale=True)
    with open(
        os.path.join(os.path.dirname(file_path), "assets/registry/server.jar"), "wb"
    ) as f:
        for chunk in res.iter_content(chunk_size=1024):
            f.write(chunk)
            progress.update(len(chunk))
        progress.close()
