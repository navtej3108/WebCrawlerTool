import tkinter as tk
from tkinter import messagebox
from urllib.parse import urlparse, parse_qs, urljoin
from bs4 import BeautifulSoup
import requests
import pandas as pd
import os


class WebCrawlerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Web Crawler Tool")
        self.root.geometry("600x400")

        self.urls = []

        # UI elements for URL input
        self.url_frame = tk.Frame(root)
        self.url_frame.pack(pady=20)

        self.add_url_button = tk.Button(root, text="Add URL", command=self.add_url_entry)
        self.add_url_button.pack(pady=10)

        self.start_button = tk.Button(root, text="Start Crawling", command=self.start_crawl)
        self.start_button.pack(pady=10)

    def add_url_entry(self):
        url_entry = tk.Entry(self.url_frame, width=50)
        url_entry.pack(pady=5)
        self.urls.append(url_entry)

    def start_crawl(self):
        if not self.urls:
            messagebox.showerror("Error", "Please add at least one URL")
            return
        
        # Get URLs entered by the user
        urls = [url.get() for url in self.urls if url.get().strip()]
        if not urls:
            messagebox.showerror("Error", "Please enter valid URLs")
            return

        # Start the crawling process
        parameters = []
        for url in urls:
            parameters.extend(self.crawl_and_extract_parameters(url))

        if parameters:
            self.ask_to_save_window(parameters)  # Open the new window for save options
            self.root.withdraw()  # Hide the main window (instead of destroying it)
        else:
            messagebox.showerror("Error", "No parameters found or unable to crawl the URLs.")

    def crawl_and_extract_parameters(self, url):
        parameters = []
        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                links = soup.find_all('a', href=True)

                for link in links:
                    link_url = link['href']
                    link_url = urljoin(url, link_url)
                    parsed_link_url = urlparse(link_url)
                    link_domain = parsed_link_url.netloc

                    if link_domain == domain:
                        query_params = parse_qs(parsed_link_url.query)
                        if query_params:
                            parameters.append({
                                'url': link_url,
                                'parameters': query_params
                            })
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

        return parameters

    def ask_to_save_window(self, parameters):
        save_window = tk.Toplevel(self.root)
        save_window.title("Save Options")
        save_window.geometry("400x200")

        # Save as HTML
        save_html_button = tk.Button(save_window, text="Save as HTML", command=lambda: self.save_to_html(parameters, save_window))
        save_html_button.pack(pady=10)

        # Save as Excel
        save_excel_button = tk.Button(save_window, text="Save as Excel", command=lambda: self.save_to_excel(parameters, save_window))
        save_excel_button.pack(pady=10)

        # Save as Text
        save_text_button = tk.Button(save_window, text="Save as Text", command=lambda: self.save_to_text(parameters, save_window))
        save_text_button.pack(pady=10)

        # Save as All
        save_all_button = tk.Button(save_window, text="Save as All", command=lambda: self.save_all(parameters, save_window))
        save_all_button.pack(pady=10)

    def save_to_html(self, parameters, window):
        self.save_to_file(parameters, 'html', window)

    def save_to_excel(self, parameters, window):
        self.save_to_file(parameters, 'excel', window)

    def save_to_text(self, parameters, window):
        self.save_to_file(parameters, 'text', window)

    def save_all(self, parameters, window):
        self.save_to_file(parameters, 'html', window)
        self.save_to_file(parameters, 'excel', window)
        self.save_to_file(parameters, 'text', window)

    def save_to_file(self, parameters, file_type, window):
        if file_type == 'html':
            output_html = "<html>\n"
            output_html += "<body>\n"
            output_html += "<h2>Extracted URL Parameters</h2>\n"
            output_html += "<table border='1'>\n"
            output_html += "<tr>\n<th>URL</th>\n<th>Parameters</th>\n</tr>\n"

            for param in parameters:
                output_html += f"<tr>\n<td>{param['url']}</td>\n<td>{str(param['parameters'])}</td>\n</tr>\n"

            output_html += "</table>\n"
            output_html += "</body>\n"
            output_html += "</html>\n"

            with open("output.html", "w") as file:
                file.write(output_html)

        elif file_type == 'excel':
            data = []
            for param in parameters:
                data.append({
                    'URL': param['url'],
                    'Parameters': str(param['parameters'])
                })

            df = pd.DataFrame(data)
            df.to_excel('output.xlsx', index=False)

        elif file_type == 'text':
            with open("output.txt", "w") as file:
                for param in parameters:
                    file.write(f"URL: {param['url']}\n")
                    file.write(f"Parameters: {str(param['parameters'])}\n\n")

        messagebox.showinfo("Success", f"Results saved to 'output.{file_type}'")
        window.destroy()  # Close the save options window
        self.exit_button()

    def exit_button(self):
        exit_window = tk.Toplevel(self.root)
        exit_window.title("Exit")
        exit_window.geometry("300x100")

        exit_button = tk.Button(exit_window, text="Exit", command=self.root.quit)
        exit_button.pack(pady=20)


if __name__ == "__main__":
    root = tk.Tk()
    app = WebCrawlerApp(root)
    root.mainloop()
