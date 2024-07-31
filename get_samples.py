from datetime import datetime, timedelta
import os
import yara
import shutil
import zipfile
import requests
import subprocess

MALWARE_DIRECTORY = "./samples/"


def download(file_url: str, filename: str):
    """
    Downloads given file to a given location.

    params:
    file_url: str -> url of the file to download
    filename: str -> Name and location of the downloaded file
    """
    with open(filename, "wb") as file:

        response = requests.get(file_url, stream=True)
        total_length = response.headers.get("content-length")

        if total_length is None:
            file.write(response.content)

        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                file.write(data)
                done = int(50 * dl / total_length)
                percentage = int((dl / total_length) * 100)
                print(
                    f"[{'=' * done}{' ' * (50 - done)}] {percentage}%",
                    end="\r",
                    flush=True,
                )
    print()
    print(f"[+] Downloaded {filename}")


def download_malwares(custom_date="False"):
    """
    Downloads elfs from bazaar's daily repo.
    """
    bazaar_daily_url = "https://datalake.abuse.ch/malware-bazaar/daily/"

    if custom_date == "False":
        current_date = datetime.now()
        yesterday = current_date - timedelta(days=1)
        yesterday_date = yesterday.strftime("%Y-%m-%d")
        date = yesterday_date
    else:
        date = custom_date

    zipname = f"{date}.zip"
    zippath = MALWARE_DIRECTORY + zipname

    download(
        bazaar_daily_url + zipname,
        zippath,
    )
    try:
        with zipfile.ZipFile(zippath, "r") as zipfile_:
            i = 0
            for file in zipfile_.namelist():
                if ".exe" in file:
                    zipfile_.extract(file, MALWARE_DIRECTORY, pwd=b"infected")

                    i += 1
                    print(f"[*] Retrieved {i} samples", end="\r", flush=True)
    except zipfile.BadZipFile:
        try:
            os.remove(zippath)
        except FileNotFoundError:
            print("[!] No zip file found.")
            return

    print()

    try:
        os.remove(zippath)
    except FileNotFoundError:
        print("[!] No zip file found.")
        return


def detect_nsis_and_electron():
    rule = yara.compile(filepath="./rules/nsis.yara")

    for exe in os.listdir(MALWARE_DIRECTORY):
        matched = rule.match(MALWARE_DIRECTORY + exe)
        if len(matched) != 0:
            try:
                output = subprocess.check_output(
                    [
                        "7z",
                        "l",
                        MALWARE_DIRECTORY + exe,
                    ]
                )
            except subprocess.CalledProcessError:
                continue
            if b"app-64.7z" in output:
                shutil.copy(MALWARE_DIRECTORY + exe, f"./nsis/{exe}")
                print(f"Found positive match with {exe}")


def extract_asar():
    for exe in os.listdir("./nsis"):
        if ".exe" in exe:
            subprocess.check_output(
                ["7z", "e", f"./nsis/{exe}", "-onsis", "$PLUGINSDIR/app-64.7z"],
                stderr=subprocess.STDOUT,
            )

            subprocess.check_output(
                [
                    "7z",
                    "e",
                    "./nsis/app-64.7z",
                    f"-onsis/{exe[:-4]}",
                    "resources/app.asar",
                ],
                stderr=subprocess.STDOUT,
            )
            os.system(rf"mv ./nsis/{exe} ./nsis/{exe[:-4]}")
            os.system(f"rm ./nsis/app-64.7z")


def cleanup():
    os.system("rm ./samples/*")


def main():
    for j in range(1, 31):
        date = f"2024-07-{str(j).zfill(2)}"

        print(f"Downloading {date}.zip")
        download_malwares(date)

        detect_nsis_and_electron()

        extract_asar()

        cleanup()


if __name__ == "__main__":
    main()
