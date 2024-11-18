import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import tkinter as tk
from tkinter import filedialog, messagebox
import re
import logging


# Set up logging for Selenium WebDriver
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Function to download images
def download_images(url, save_folder):
    # Set up Selenium WebDriver options
    options = Options()
    options.add_argument("--headless")  # Run in headless mode (without opening a browser window)
    service = Service(ChromeDriverManager().install())

    # Start WebDriver
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)

    # Scroll to the bottom of the page to load more content
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for content to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Get page source after scrolling
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    # Find and download images
    image_containers = soup.find_all('div', class_='slide-image-container')
    count = 0
    for container in image_containers:
        img_tag = container.find('img')
        if img_tag:
            img_url = img_tag.get('src')
            if img_url and img_url.startswith('//'):
                img_url = 'https:' + img_url
            
            # Extract the numbers right after ".suffix" in the image URL using regex
            match = re.search(r'\.suffix/(\d+)\.', img_url)
            if match:
                img_name = f"{match.group(1)}.jpg"
            else:
                img_name = f"image_{count}.jpg"
            
            try:
                img_response = requests.get(img_url)
                img_response.raise_for_status()
                
                with open(os.path.join(save_folder, img_name), 'wb') as img_file:
                    img_file.write(img_response.content)
                count += 1
            except requests.exceptions.RequestException as e:
                print(f"Failed to download {img_url}: {e}")

    if count > 0:
        messagebox.showinfo("Success", f"Downloaded {count} images to {save_folder}")
    else:
        messagebox.showinfo("Info", "No images found to download.")

# Function to choose save directory and start download
def choose_directory_and_download():
    url = url_entry.get()
    if not url:
        messagebox.showwarning("Input Error", "Please enter a URL.")
        return
    
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        download_images(url, folder_selected)

# Set up the Tkinter GUI
root = tk.Tk()
root.title("Image Downloader")

frame = tk.Frame(root)
frame.pack(pady=10)

url_label = tk.Label(frame, text="Enter URL:")
url_label.pack(side="left")
url_entry = tk.Entry(frame, width=50)
url_entry.pack(side="left", padx=5)

download_button = tk.Button(root, text="Choose Directory and Download", command=choose_directory_and_download)
download_button.pack(pady=10)

root.mainloop()
