import json
import os
import re
import sqlite3
import time
import tkinter as tk
import webbrowser
import sys
from datetime import datetime
from json import JSONDecodeError
from tkinter import ttk
from tkinter.font import Font
from typing import Union

import pyperclip
import requests
from requests.auth import HTTPProxyAuth
import urllib3
from lxml import html, etree
import atexit

import config
import login_data
from custom_widgets import MyText, MyLabel, MyFrame, MyButton, MyCheckbutton, MyRadiobutton
import dropbox_methods


# TODO: Settings Page
# TODO: Custom Clipboard
# TODO: Popular Regex
# TODO: Tooltips
# TODO: Documentation


class MainApplication(tk.Tk):
    def __init__(self):
        t1 = time.time()
        super().__init__()
        self.kraken_id = ""
        self.all_widgets = []
        self.last_tree = {'link': '', 'tree': ''}
        self.session = requests.Session()
        self.headers = config.default_login_header
        self.title(config.window_title)
        self.set_word_boundaries()
        self.configure(background=config.background)
        self.current_view = 'extractor'
        self.debug_mode = True if len(sys.argv) > 1 and sys.argv[1] == 'debug' else False
        if self.debug_mode:
            print('________________DEBUG MODE__________________________')
        self.general_style = self.frame_style = self.checkbutton_style = self.label_style = self.label_style_bold = self.button_style = self.button_style_bold = ttk.Style()
        self.general_style.theme_use('clam')
        self.frame_style.configure('TFrame', background=config.background)
        self.checkbutton_style.configure('TCheckbutton', background=config.background)
        self.label_style.configure('TLabel', background=config.background, font=(config.label_font, 9))
        self.label_style.configure('TRadiobutton', background=config.background, font=(config.label_font, 9))
        self.label_style_bold.configure('Bold.TLabel', background=config.background, font=(config.label_font, 9, 'bold'))
        self.button_style.configure('TButton', font=(config.button_font, 9), width=8)
        self.button_style_bold.configure('Bold.TButton', font=(config.button_font, 10, 'bold'), width=10)
        self.text_font = Font(family=config.label_font, size=10)

        # Extractor Frames (Order chosen here)
        self.view_menu_frame = MyFrame(master=self, padding=5, view='menu')
        self.info_frame = MyFrame(master=self, view='extractor')
        self.kraken_frame = MyFrame(master=self, view='extractor')
        self.json_full_frame = MyFrame(master=self, view='extractor')
        self.json_combined_buttons_frame = MyFrame(master=self.json_full_frame, view='extractor')
        self.json_buttons_frame = MyFrame(master=self.json_combined_buttons_frame, view='extractor')
        self.json_checkbutton_frame = MyFrame(self.json_combined_buttons_frame, view='extractor')
        self.start_urls_frame = MyFrame(master=self, view='extractor')
        self.menu_frame = MyFrame(master=self, view='extractor')
        self.articles_frame = MyFrame(master=self, view='extractor')
        self.title_frame = MyFrame(master=self, view='extractor')
        self.pubdate_frame = MyFrame(master=self, view='extractor')
        self.pubdate_buttons_frame = MyFrame(master=self.pubdate_frame, view='extractor')
        self.author_frame = MyFrame(master=self, view='extractor')
        self.body_frame = MyFrame(master=self, view='extractor')
        self.body_buttons_frame = MyFrame(self.body_frame, view='extractor')
        self.sitemap_frame = MyFrame(master=self, view='extractor')
        self.sitemap_buttons_frame = MyFrame(self.sitemap_frame, view='extractor')
        self.link_regex_frame = MyFrame(master=self, view='extractor')
        self.link_regex_buttons_frame = MyFrame(self.link_regex_frame, view='extractor')
        self.bottom_buttons_frame = MyFrame(master=self, view='extractor')

        # Finder Frames (Order chosen here)
        self.finder_filter_frame = MyFrame(master=self, view='finder', padding=10)
        self.article_url_frame = MyFrame(master=self, view='finder', padding=10)
        self.finder_title_frame = MyFrame(master=self, view='finder', padding=10)
        self.finder_pubdate_frame = MyFrame(master=self, view='finder', padding=10)
        self.finder_author_frame = MyFrame(master=self, view='finder', padding=10)
        self.finder_body_frame = MyFrame(master=self, view='finder', padding=10)
        self.finder_image_frame = MyFrame(master=self, view='finder', padding=10)
        self.junk_xpath_body_frame = MyFrame(master=self, view='finder', padding=10)
        self.finder_junk_frame = MyFrame(master=self, view='finder', padding=10)

        # Menu Labels
        self.info_label = MyLabel(master=self.view_menu_frame, view='menu', text="", width=70, justify=tk.CENTER, style='Bold.TLabel', anchor='center')

        # Extractor Labels
        self.kraken_id_label = MyLabel(master=self.kraken_frame, view='extractor', text="Kraken Link/ID:")
        self.json_label = MyLabel(master=self.json_full_frame, view='extractor', text="JSON:")
        self.start_urls_label = MyLabel(master=self.start_urls_frame, view='extractor', text="Start URLs:")
        self.menu_label = MyLabel(master=self.menu_frame, view='extractor', text="Menu XPath:")
        self.articles_label = MyLabel(master=self.articles_frame, view='extractor', text="Articles XPath:")
        self.title_label = MyLabel(master=self.title_frame, view='extractor', text="Title XPath:")
        self.pubdate_label = MyLabel(master=self.pubdate_frame, view='extractor', text="Pubdate XPath:")
        self.author_label = MyLabel(master=self.author_frame, view='extractor', text="Author XPath:")
        self.body_label = MyLabel(master=self.body_frame, view='extractor', text="Body XPath:")
        self.sitemap_label = MyLabel(master=self.sitemap_frame, view='extractor', text="Sitemap Links:")
        self.link_regex_label = MyLabel(master=self.link_regex_frame, view='extractor', text="Link Regex Id:")
        self.last_extractor_user_label = MyLabel(master=self.info_frame, view='extractor', text="Last user(Extractor):", width=20)
        self.last_kraken_user_label = MyLabel(master=self.info_frame, view='extractor', text="Last user(Kraken):", width=20)
        self.domain_label = MyLabel(master=self.info_frame, view='extractor', text="Domain:", width=20)
        self.status_label = MyLabel(master=self.info_frame, view='extractor', text="Status:", width=15)
        self.projects_label = MyLabel(master=self.info_frame, view='extractor', text="List of Projects:", width=15)
        self.name_label = MyLabel(master=self.info_frame, view='extractor', text="Name:", width=15)
        self.botname_label = MyLabel(master=self.info_frame, view='extractor', text="Botname:", width=10)

        self.date_order_label = MyLabel(master=self.json_buttons_frame, view='extractor', text="")
        self.last_extractor_user_var_label = MyLabel(master=self.info_frame, view='extractor', text="", width=35, style='Bold.TLabel')
        self.last_kraken_user_var_label = MyLabel(master=self.info_frame, view='extractor', text="", width=35, style='Bold.TLabel')

        self.domain_var_label = MyLabel(master=self.info_frame, view='extractor', text="", width=35, style='Bold.TLabel')
        self.projects_var_label = MyLabel(master=self.info_frame, view='extractor', text="", width=20, style='Bold.TLabel')
        self.name_var_label = MyLabel(master=self.info_frame, view='extractor', text="", width=20, style='Bold.TLabel')
        self.botname_var_label = MyLabel(master=self.info_frame, view='extractor', text="", width=20, style='Bold.TLabel')
        self.status_var_label = MyLabel(master=self.info_frame, view='extractor', text="", width=20, style='Bold.TLabel')

        self.var_labels = [self.date_order_label, self.last_extractor_user_var_label, self.last_kraken_user_var_label, self.domain_var_label,
                           self.status_var_label, self.projects_var_label, self.name_var_label, self.botname_var_label, self.info_label]

        # Finder Labels
        self.finder_filter_label = MyLabel(master=self.finder_filter_frame, view='finder', text="Multiple Results Filter:", width=25)
        self.finder_article_label = MyLabel(master=self.article_url_frame, view='finder', text="URL:", width=15)
        self.finder_title_label = MyLabel(master=self.finder_title_frame, view='finder', text="Title XPath:", width=15)
        self.finder_pubdate_label = MyLabel(master=self.finder_pubdate_frame, view='finder', text="Pubdate XPath:", width=15)
        self.finder_author_label = MyLabel(master=self.finder_author_frame, view='finder', text="Author XPath:", width=15)
        self.finder_body_label = MyLabel(master=self.finder_body_frame, view='finder', text="Body XPath:", width=15)
        self.finder_image_label = MyLabel(master=self.finder_image_frame, view='finder', text="Image XPath:", width=15)
        self.junk_body_label = MyLabel(master=self.junk_xpath_body_frame, view='finder', text="Body to clean:", width=15)
        self.junk_body_elements_label = MyLabel(master=self.junk_xpath_body_frame, view='finder', text="", width=25)
        self.finder_junk_label = MyLabel(master=self.finder_junk_frame, view='finder', text="Junk found:", width=15)

        # Extractor Textboxes
        self.kraken_textbox = MyText(master=self.kraken_frame, view='extractor', height=2, width=60)
        self.json_textbox = MyText(master=self.json_full_frame, view='extractor', height=8, width=60)
        self.start_urls_textbox = MyText(master=self.start_urls_frame, view='extractor', height=2, width=60)
        self.menu_textbox = MyText(master=self.menu_frame, view='extractor', height=2, width=60)
        self.articles_textbox = MyText(master=self.articles_frame, view='extractor', height=2, width=60)
        self.title_textbox = MyText(master=self.title_frame, view='extractor', height=2, width=60)
        self.pubdate_textbox = MyText(master=self.pubdate_frame, view='extractor', height=3, width=60)
        self.author_textbox = MyText(master=self.author_frame, view='extractor', height=2, width=60)
        self.body_textbox = MyText(master=self.body_frame, view='extractor', height=3, width=60)
        self.sitemap_textbox = MyText(master=self.sitemap_frame, view='extractor', height=2, width=60)
        self.link_regex_textbox = MyText(master=self.link_regex_frame, view='extractor', height=2, width=60)

        self.xpath_dict = {
            "start_urls": self.start_urls_textbox,
            "menu_xpath": self.menu_textbox,
            "articles_xpath": self.articles_textbox,
            "title_xpath": self.title_textbox,
            "pubdate_xpath": self.pubdate_textbox,
            "author_xpath": self.author_textbox,
            "body_xpath": self.body_textbox,
            "sitemap_urls": self.sitemap_textbox,
            "link_id_regex": self.link_regex_textbox,
        }

        # Finder Textboxes
        self.finder_article_textbox = MyText(master=self.article_url_frame, view='finder', height=1, width=81)
        self.finder_junk_textbox = MyText(master=self.junk_xpath_body_frame, view='finder', height=2, width=60)
        self.finder_title_xpath_1 = MyText(master=self.finder_title_frame, view='finder', height=1, width=40)
        self.finder_title_xpath_2 = MyText(master=self.finder_title_frame, view='finder', height=1, width=40)
        self.finder_title_xpath_3 = MyText(master=self.finder_title_frame, view='finder', height=1, width=40)
        self.finder_title_xpath_4 = MyText(master=self.finder_title_frame, view='finder', height=1, width=40)
        self.finder_title_result_1 = MyText(master=self.finder_title_frame, view='finder', height=1, width=40)
        self.finder_title_result_2 = MyText(master=self.finder_title_frame, view='finder', height=1, width=40)
        self.finder_title_result_3 = MyText(master=self.finder_title_frame, view='finder', height=1, width=40)
        self.finder_title_result_4 = MyText(master=self.finder_title_frame, view='finder', height=1, width=40)
        self.finder_pubdate_xpath_1 = MyText(master=self.finder_pubdate_frame, view='finder', height=1, width=40)
        self.finder_pubdate_xpath_2 = MyText(master=self.finder_pubdate_frame, view='finder', height=1, width=40)
        self.finder_pubdate_xpath_3 = MyText(master=self.finder_pubdate_frame, view='finder', height=1, width=40)
        self.finder_pubdate_xpath_4 = MyText(master=self.finder_pubdate_frame, view='finder', height=1, width=40)
        self.finder_pubdate_result_1 = MyText(master=self.finder_pubdate_frame, view='finder', height=1, width=40)
        self.finder_pubdate_result_2 = MyText(master=self.finder_pubdate_frame, view='finder', height=1, width=40)
        self.finder_pubdate_result_3 = MyText(master=self.finder_pubdate_frame, view='finder', height=1, width=40)
        self.finder_pubdate_result_4 = MyText(master=self.finder_pubdate_frame, view='finder', height=1, width=40)
        self.finder_author_xpath_1 = MyText(master=self.finder_author_frame, view='finder', height=1, width=40)
        self.finder_author_xpath_2 = MyText(master=self.finder_author_frame, view='finder', height=1, width=40)
        self.finder_author_xpath_3 = MyText(master=self.finder_author_frame, view='finder', height=1, width=40)
        self.finder_author_xpath_4 = MyText(master=self.finder_author_frame, view='finder', height=1, width=40)
        self.finder_author_result_1 = MyText(master=self.finder_author_frame, view='finder', height=1, width=40)
        self.finder_author_result_2 = MyText(master=self.finder_author_frame, view='finder', height=1, width=40)
        self.finder_author_result_3 = MyText(master=self.finder_author_frame, view='finder', height=1, width=40)
        self.finder_author_result_4 = MyText(master=self.finder_author_frame, view='finder', height=1, width=40)
        self.finder_body_xpath_1 = MyText(master=self.finder_body_frame, view='finder', height=1, width=40)
        self.finder_body_xpath_2 = MyText(master=self.finder_body_frame, view='finder', height=1, width=40)
        self.finder_body_xpath_3 = MyText(master=self.finder_body_frame, view='finder', height=1, width=40)
        self.finder_body_xpath_4 = MyText(master=self.finder_body_frame, view='finder', height=1, width=40)
        self.finder_body_result_1 = MyText(master=self.finder_body_frame, view='finder', height=1, width=40)
        self.finder_body_result_2 = MyText(master=self.finder_body_frame, view='finder', height=1, width=40)
        self.finder_body_result_3 = MyText(master=self.finder_body_frame, view='finder', height=1, width=40)
        self.finder_body_result_4 = MyText(master=self.finder_body_frame, view='finder', height=1, width=40)
        self.finder_image_xpath_1 = MyText(master=self.finder_image_frame, view='finder', height=1, width=40)
        self.finder_image_xpath_2 = MyText(master=self.finder_image_frame, view='finder', height=1, width=40)
        self.finder_image_xpath_3 = MyText(master=self.finder_image_frame, view='finder', height=1, width=40)
        self.finder_image_xpath_4 = MyText(master=self.finder_image_frame, view='finder', height=1, width=40)
        self.finder_image_result_1 = MyText(master=self.finder_image_frame, view='finder', height=1, width=40)
        self.finder_image_result_2 = MyText(master=self.finder_image_frame, view='finder', height=1, width=40)
        self.finder_image_result_3 = MyText(master=self.finder_image_frame, view='finder', height=1, width=40)
        self.finder_image_result_4 = MyText(master=self.finder_image_frame, view='finder', height=1, width=40)
        self.finder_junk_xpath_1 = MyText(master=self.finder_junk_frame, view='finder', height=1, width=40)
        self.finder_junk_xpath_2 = MyText(master=self.finder_junk_frame, view='finder', height=1, width=40)
        self.finder_junk_xpath_3 = MyText(master=self.finder_junk_frame, view='finder', height=1, width=40)
        self.finder_junk_xpath_4 = MyText(master=self.finder_junk_frame, view='finder', height=1, width=40)
        self.finder_junk_result_1 = MyText(master=self.finder_junk_frame, view='finder', height=1, width=40)
        self.finder_junk_result_2 = MyText(master=self.finder_junk_frame, view='finder', height=1, width=40)
        self.finder_junk_result_3 = MyText(master=self.finder_junk_frame, view='finder', height=1, width=40)
        self.finder_junk_result_4 = MyText(master=self.finder_junk_frame, view='finder', height=1, width=40)

        # View Menu Buttons
        self.open_extractor_button = MyButton(master=self.view_menu_frame, view='menu', text="Extractor", command=lambda: self.switch_view(view_to_open='extractor'))
        self.open_finder_button = MyButton(master=self.view_menu_frame, view='menu', text="Finder", command=lambda: self.switch_view(view_to_open='finder'))
        self.sync_button = MyButton(master=self.view_menu_frame, view='menu', text="Sync", command=dropbox_methods.download_db)
        self.refresh_db_button = MyButton(master=self.view_menu_frame, view='menu', text="Refresh DB", command=self.update_finder_tables)

        # Kraken Buttons
        self.kraken_clipboard_button = MyButton(master=self.kraken_frame, view='extractor', text="Clipboard", command=lambda: self.load_from_kraken(self.clipboard_get().strip()))
        self.open_source_button = MyButton(master=self.kraken_frame, view='extractor', text="Source", command=lambda: self.open_link(self.get_strip(self.kraken_textbox)))
        self.load_from_db_button = MyButton(master=self.kraken_frame, view='extractor', text="DB Load", command=self.load_from_db)
        self.open_items_button = MyButton(master=self.kraken_frame, view='extractor', text="Items", command=self.open_items_page)

        # JSON Buttons
        self.code_copy_button = MyButton(master=self.json_buttons_frame, view='extractor', text="Copy", command=lambda: self.copy_code(self.json_textbox))
        self.load_from_existing_button = MyButton(master=self.json_buttons_frame, view='extractor', text="Load", command=lambda: self.generate(load_from_existing_bool=True))
        self.load_without_url_button = MyButton(master=self.json_buttons_frame, view='extractor', text="Load (-URL)",
                                                command=lambda: self.generate(load_from_existing_bool=True, leave_current_url=True))
        self.add_proxy_button = MyButton(master=self.json_buttons_frame, view='extractor', text="Proxy", command=lambda: self.edit_json(initial_key="scrapy_settings",
                                                                                                                                        keyword="HTTP_PROXY",
                                                                                                                                        value=config.proxy_for_source))
        self.allowed_domains_button = MyButton(master=self.json_buttons_frame, view='extractor', text="Alw. Dom.", command=lambda: self.edit_json(initial_key="scrapy_arguments",
                                                                                                                                                  keyword="allowed_domains",
                                                                                                                                                  value=self.get_source_name(
                                                                                                                                                      copy=False)))
        self.pubdate_required_button = MyButton(master=self.json_buttons_frame, view='extractor', text="Pubdate Req", command=lambda: self.edit_json(initial_key="scrapy_arguments",
                                                                                                                                                     keyword="pubdate_required",
                                                                                                                                                     value=True))
        self.init_wait_button = MyButton(master=self.json_buttons_frame, view='extractor', text="Init Wait", command=lambda: self.edit_json(initial_key="scrapy_arguments",
                                                                                                                                            keyword='init_wait', value=2))
        self.article_wait_button = MyButton(master=self.json_buttons_frame, view='extractor', text="Article Wait", command=lambda: self.edit_json(initial_key="scrapy_arguments",
                                                                                                                                                  keyword='article_wait', value=2))

        # Date Order Buttons
        self.date_order_DMY = MyButton(master=self.json_buttons_frame, view='extractor', text="DMY", command=lambda: self.edit_json(initial_key="scrapy_arguments",
                                                                                                                                    keyword='date_order', value='DMY'))
        self.date_order_YMD = MyButton(master=self.json_buttons_frame, view='extractor', text="YMD", command=lambda: self.edit_json(initial_key="scrapy_arguments",
                                                                                                                                    keyword='date_order', value='YMD'))
        self.date_order_MDY = MyButton(master=self.json_buttons_frame, view='extractor', text="MDY", command=lambda: self.edit_json(initial_key="scrapy_arguments",
                                                                                                                                    keyword='date_order', value='MDY'))

        # JSON Checkbuttons
        self.open_links_check_bool = tk.IntVar()
        self.overwrite_domain_check_bool = tk.IntVar()
        self.rdc_check_bool = tk.IntVar()

        # Set starting values
        self.open_links_check_bool.set(1)
        self.overwrite_domain_check_bool.set(1)
        self.rdc_check_bool.set(0)

        self.open_source_checkbutton = MyCheckbutton(master=self.json_checkbutton_frame, view='extractor', text="Auto Open Source", variable=self.open_links_check_bool)
        self.overwrite_domain_checkbutton = MyCheckbutton(master=self.json_checkbutton_frame, view='extractor', text="Overwrite Domain", variable=self.overwrite_domain_check_bool)
        self.rdc_checkbutton = MyCheckbutton(master=self.json_checkbutton_frame, view='extractor', text="RDC", variable=self.rdc_check_bool)

        # Start URL Buttons
        self.copy_start_button = MyButton(master=self.start_urls_frame, view='extractor', text="Copy", command=lambda: self.copy_code(self.start_urls_textbox))
        self.open_link_button = MyButton(master=self.start_urls_frame, view='extractor', text='Open Link', command=self.open_start_urls_link)
        self.open_domain_button = MyButton(master=self.start_urls_frame, view='extractor', text='Open Dmn', command=self.open_domain)
        self.source_name_button = MyButton(master=self.start_urls_frame, view='extractor', text="Copy Name", command=self.get_source_name)
        self.source_domain_button = MyButton(master=self.start_urls_frame, view='extractor', text="Copy Dmn", command=lambda: self.get_domain(copy=True))

        # Menu Buttons
        self.copy_menu_button = MyButton(master=self.menu_frame, view='extractor', text="Copy", command=lambda: self.copy_code(self.menu_textbox))
        self.menu_category_button = MyButton(master=self.menu_frame, view='extractor', text="Cat",
                                             command=lambda: self.append_textbox_values(self.menu_textbox, after_value="[contains(@href, 'ategor')]"))

        # Article Xpath Buttons
        self.copy_articles_button = MyButton(master=self.articles_frame, view='extractor', text="Copy", command=lambda: self.copy_code(self.articles_textbox))
        self.article_not_category_button = MyButton(master=self.articles_frame, view='extractor', text="Not Href",
                                                    command=lambda: self.append_textbox_values(self.articles_textbox,
                                                                                               before_value='(', after_value=")[not(contains(@href, 'ategor'))]"))
        self.article_cont_href_button = MyButton(master=self.articles_frame, view='extractor', text="Cont Href",
                                                 command=lambda: self.replace_textbox_value(self.articles_textbox, "//a[contains(@href, 'BLANK')]"))
        self.article_title_button = MyButton(master=self.articles_frame, view='extractor', text="Cont Title",
                                             command=lambda: self.replace_textbox_value(self.articles_textbox, "//*[contains(@class,'title')]/a"))
        self.article_recent_button = MyButton(master=self.articles_frame, view='extractor', text="Recent",
                                             command=lambda: self.append_textbox_values(self.articles_textbox,
                                                                                        after_value=" | //*[contains(@*,'recent-posts-')]//a"))

        # Title Xpath Buttons
        self.copy_title_button = MyButton(master=self.title_frame, view='extractor', text="Copy", command=lambda: self.copy_code(self.title_textbox))
        self.title_single_button = MyButton(master=self.title_frame, view='extractor', text="[1]",
                                            command=lambda: self.append_textbox_values(self.title_textbox, before_value='(', after_value=')[1]'))
        self.title_h1_button = MyButton(master=self.title_frame, view='extractor', text="h1",
                                        command=lambda: self.replace_textbox_value(self.title_textbox, "//h1[contains(@class,'title')]"))

        # Pubdate Xpath Buttons
        self.copy_pubdate_button = MyButton(master=self.pubdate_buttons_frame, view='extractor', text="Copy", command=lambda: self.copy_code(self.pubdate_textbox))
        self.pubdate_single_button = MyButton(master=self.pubdate_buttons_frame, view='extractor', text="[1]", command=lambda: self.append_textbox_values(self.pubdate_textbox,
                                                                                                                                                          before_value='(',
                                                                                                                                                          after_value=')[1]'))
        self.standard_regex_button = MyButton(master=self.pubdate_buttons_frame, view='extractor', text="1.1.2022",
                                              command=lambda: self.append_textbox_values(self.pubdate_textbox,
                                                                                         before_value="re:match(", after_value=r", '\d{1,2}\.\s*\d{1,2}\.\s*\d{2,4}', 'g')"))
        self.reverse_regex_button = MyButton(master=self.pubdate_buttons_frame, view='extractor', text="2022.1.1",
                                             command=lambda: self.append_textbox_values(self.pubdate_textbox, before_value="re:match(",
                                                                                        after_value=r", '\d{2,4}\.\s*\d{1,2}\.\s*\d{1,2}', 'g')"))
        self.word_dot_regex_button = MyButton(master=self.pubdate_buttons_frame, view='extractor', text="21. Jan 2022",
                                              command=lambda: self.append_textbox_values(self.pubdate_textbox, before_value="re:match(",
                                                                                         after_value=r", '(\d{2,4})\.(\s\w+\s\d{1,2})', 'g')"))
        self.blank_regex_button = MyButton(master=self.pubdate_buttons_frame, view='extractor', text="Rgx Blank",
                                           command=lambda: self.append_textbox_values(self.pubdate_textbox, before_value="re:match(",
                                                                                      after_value=r", 'REGEX', 'g')"))

        self.date_meta = "(((//meta[contains(@*, 'date')] | //meta[contains(@*, 'time')] | //*[contains(@*, 'datePublished')])[1]/@content) | //time/@datetime)[1]"
        self.meta_button = MyButton(master=self.pubdate_buttons_frame, view='extractor', text="Meta",
                                    command=lambda: self.replace_textbox_value(self.pubdate_textbox, self.date_meta))
        self.pubdate_replace_button = MyButton(master=self.pubdate_buttons_frame, view='extractor', text="Replace",
                                               command=lambda: self.append_textbox_values(self.pubdate_textbox, before_value="re:replace(",
                                                                                          after_value=r", 'SYMBOL1', 'g', 'SYMBOL2')"))
        self.word_regex_button = MyButton(master=self.pubdate_buttons_frame, view='extractor', text="Rgx Word",
                                          command=lambda: self.append_textbox_values(self.pubdate_textbox, before_value="re:match(",
                                                                                     after_value=r", '\d{1,2}\s\w+\s\d{2,4}', 'g')"))
        self.pubdate_copy_without_regex = MyButton(master=self.pubdate_buttons_frame, view='extractor', text="Copy NoRgx",
                                                   command=lambda: pyperclip.copy(self.extract_xpath_from_regex(self.get_strip(self.pubdate_textbox))))

        # Author Xpath Buttons
        self.copy_author_button = MyButton(master=self.author_frame, view='extractor', text="Copy", command=lambda: self.copy_code(self.author_textbox))
        self.author_single_button = MyButton(master=self.author_frame, view='extractor', text="[1]",
                                             command=lambda: self.append_textbox_values(self.author_textbox, before_value='(', after_value=')[1]'))
        self.author_substring_button = MyButton(master=self.author_frame, view='extractor', text="Substring",
                                                command=lambda: self.append_textbox_values(self.author_textbox, before_value="substring-after(",
                                                                                           after_value=", ':')"))
        self.author_meta_button = MyButton(master=self.author_frame, view='extractor', text="Meta",
                                           command=lambda: self.replace_textbox_value(self.author_textbox, "//meta[contains(@*,'uthor')]/@content"))
        self.author_child_text_button = MyButton(master=self.author_frame, view='extractor', text="Child",
                                                 command=lambda: self.replace_textbox_value(self.author_textbox, '//*[child::text()[contains(.,"Autor")]]'))
        # Body Xpath MyButtons
        self.body_single_button = MyButton(master=self.body_buttons_frame, view='extractor', text="[1]",
                                           command=lambda: self.append_textbox_values(self.body_textbox, before_value='(', after_value=')[1]'), )
        self.copy_body_button = MyButton(master=self.body_buttons_frame, view='extractor', text="Copy", command=lambda: self.copy_code(self.body_textbox))
        self.body_not_contains_class_button = MyButton(master=self.body_buttons_frame, view='extractor', text="Not Class",
                                                       command=lambda: self.append_textbox_values(self.body_textbox,
                                                                                                  after_value=f"[not(contains(@class, "
                                                                                                              f"'{self.clipboard_get().strip()}'))]"))
        self.body_not_contains_desc_class_button = MyButton(master=self.body_buttons_frame, view='extractor', text="Descendant",
                                                            command=lambda: self.append_textbox_values(self.body_textbox,
                                                                                                       after_value=f"[not(descendant::*[contains(@class,"
                                                                                                                   f"'{self.clipboard_get().strip()}')])]"))
        self.body_not_contains_text_button = MyButton(master=self.body_buttons_frame, view='extractor', text="Not Text",
                                                      command=lambda: self.append_textbox_values(self.body_textbox,
                                                                                                 after_value=f"[not(descendant::text()[contains(.,"
                                                                                                             f"'{self.clipboard_get().strip()}')])]"))
        self.body_not_contains_id_button = MyButton(master=self.body_buttons_frame, view='extractor', text="Not ID",
                                                    command=lambda: self.append_textbox_values(self.body_textbox,
                                                                                               after_value=f"[not(contains(@id, "
                                                                                                           f"'{self.clipboard_get().strip()}'))]"))
        self.body_not_self_button = MyButton(master=self.body_buttons_frame, view='extractor', text="Not Self",
                                             command=lambda: self.append_textbox_values(self.body_textbox,
                                                                                        after_value=f"[not(self::{self.clipboard_get().strip()})]"))
        # Sitemap Buttons
        self.copy_sitemap_button = MyButton(master=self.sitemap_buttons_frame, view='extractor', text="Copy",
                                          command=lambda: self.copy_code(self.sitemap_textbox))
        self.open_sitemap_button = MyButton(master=self.sitemap_buttons_frame, view='extractor', text='Open Link',
                                         command=self.open_sitemap_urls_link)
        self.sitemap_xml_button = MyButton(master=self.sitemap_buttons_frame,
                                           view='extractor',
                                           text="Xml",
                                           command=lambda: self.replace_textbox_value(self.sitemap_textbox, self.get_domain()+'sitemap.xml'))
        self.sitemap_html_button = MyButton(master=self.sitemap_buttons_frame,
                                              view='extractor',
                                              text="Html",
                                              command=lambda: self.replace_textbox_value(self.sitemap_textbox, self.get_domain()+'sitemap.html'))


        # Link Regex Id Buttons

        self.copy_link_regex_button = MyButton(master=self.link_regex_buttons_frame, view='extractor', text="Copy",
                                               command=lambda: self.copy_code(self.link_regex_textbox))

        self.link_regex_button = MyButton(master=self.link_regex_buttons_frame, view='extractor', text="Rgx Domain",
                                          command=lambda: self.replace_textbox_value(self.link_regex_textbox, f"^(?P<id>https?://{self.get_domain().split('//')[1]}[^?#]+)"))


        # Bottom Frame MyButtons
        self.clear_button = MyButton(master=self.bottom_buttons_frame, view='extractor', text="Clear All", command=self.clear, style='Bold.TButton')
        self.generate_button = MyButton(master=self.bottom_buttons_frame, view='extractor', text="Generate", command=self.generate, style='Bold.TButton')

        # Finder Buttons
        self.find_content_button = MyButton(master=self.article_url_frame, view='finder', text="Find", command=self.find_content, padding=0)
        self.find_junk_button = MyButton(master=self.junk_xpath_body_frame, view='finder', text="Find", command=self.find_junk, style="Bold.TButton", padding=5)
        self.add_node_button = MyButton(master=self.junk_xpath_body_frame, view='finder', text="/node()", command=lambda: self.append_textbox_values(
            textbox=self.finder_junk_textbox,
            after_value='/node()'))
        self.junk_to_body_button = MyButton(master=self.junk_xpath_body_frame, view='finder', text="Select", command=lambda: self.from_textbox_to_textbox(
            textbox_from=self.finder_junk_textbox, textboxes_to=[self.body_textbox]))

        self.title_xpath_select_button_1 = MyButton(master=self.finder_title_frame, view='finder', text="Select",
                                                    command=lambda: self.from_textbox_to_textbox(self.finder_title_xpath_1, [self.title_textbox]), padding=0)
        self.title_xpath_select_button_2 = MyButton(master=self.finder_title_frame, view='finder', text="Select",
                                                    command=lambda: self.from_textbox_to_textbox(self.finder_title_xpath_2, [self.title_textbox]), padding=0)
        self.title_xpath_select_button_3 = MyButton(master=self.finder_title_frame, view='finder', text="Select",
                                                    command=lambda: self.from_textbox_to_textbox(self.finder_title_xpath_3, [self.title_textbox]), padding=0)
        self.title_xpath_select_button_4 = MyButton(master=self.finder_title_frame, view='finder', text="Select",
                                                    command=lambda: self.from_textbox_to_textbox(self.finder_title_xpath_4, [self.title_textbox]), padding=0)

        self.pubdate_xpath_select_button_1 = MyButton(master=self.finder_pubdate_frame, view='finder', text="Select",
                                                      command=lambda: self.from_textbox_to_textbox(self.finder_pubdate_xpath_1, [self.pubdate_textbox]), padding=0)
        self.pubdate_xpath_select_button_2 = MyButton(master=self.finder_pubdate_frame, view='finder', text="Select",
                                                      command=lambda: self.from_textbox_to_textbox(self.finder_pubdate_xpath_2, [self.pubdate_textbox]), padding=0)
        self.pubdate_xpath_select_button_3 = MyButton(master=self.finder_pubdate_frame, view='finder', text="Select",
                                                      command=lambda: self.from_textbox_to_textbox(self.finder_pubdate_xpath_3, [self.pubdate_textbox]), padding=0)
        self.pubdate_xpath_select_button_4 = MyButton(master=self.finder_pubdate_frame, view='finder', text="Select",
                                                      command=lambda: self.from_textbox_to_textbox(self.finder_pubdate_xpath_4, [self.pubdate_textbox]), padding=0)

        self.author_xpath_select_button_1 = MyButton(master=self.finder_author_frame, view='finder', text="Select",
                                                     command=lambda: self.from_textbox_to_textbox(self.finder_author_xpath_1, [self.author_textbox]), padding=0)
        self.author_xpath_select_button_2 = MyButton(master=self.finder_author_frame, view='finder', text="Select",
                                                     command=lambda: self.from_textbox_to_textbox(self.finder_author_xpath_2, [self.author_textbox]), padding=0)
        self.author_xpath_select_button_3 = MyButton(master=self.finder_author_frame, view='finder', text="Select",
                                                     command=lambda: self.from_textbox_to_textbox(self.finder_author_xpath_3, [self.author_textbox]), padding=0)
        self.author_xpath_select_button_4 = MyButton(master=self.finder_author_frame, view='finder', text="Select",
                                                     command=lambda: self.from_textbox_to_textbox(self.finder_author_xpath_4, [self.author_textbox]), padding=0)

        self.body_xpath_select_button_1 = MyButton(master=self.finder_body_frame, view='finder', text="Select",
                                                   command=lambda: self.from_textbox_to_textbox(self.finder_body_xpath_1, [self.body_textbox, self.finder_junk_textbox], node='/node()'), padding=0)
        self.body_xpath_select_button_2 = MyButton(master=self.finder_body_frame, view='finder', text="Select",
                                                   command=lambda: self.from_textbox_to_textbox(self.finder_body_xpath_2, [self.body_textbox, self.finder_junk_textbox], node='/node()'), padding=0)
        self.body_xpath_select_button_3 = MyButton(master=self.finder_body_frame, view='finder', text="Select",
                                                   command=lambda: self.from_textbox_to_textbox(self.finder_body_xpath_3, [self.body_textbox, self.finder_junk_textbox], node='/node()'), padding=0)
        self.body_xpath_select_button_4 = MyButton(master=self.finder_body_frame, view='finder', text="Select",
                                                   command=lambda: self.from_textbox_to_textbox(self.finder_body_xpath_4, [self.body_textbox, self.finder_junk_textbox], node='/node()'), padding=0)

        self.image_xpath_add_button_1 = MyButton(master=self.finder_image_frame, view='finder', text="Add",
                                                 command=lambda: self.from_textbox_to_textbox(self.finder_image_xpath_1, [self.body_textbox], append_at_front=True), padding=0)
        self.image_xpath_add_button_2 = MyButton(master=self.finder_image_frame, view='finder', text="Add",
                                                 command=lambda: self.from_textbox_to_textbox(self.finder_image_xpath_2, [self.body_textbox], append_at_front=True), padding=0)
        self.image_xpath_add_button_3 = MyButton(master=self.finder_image_frame, view='finder', text="Add",
                                                 command=lambda: self.from_textbox_to_textbox(self.finder_image_xpath_3, [self.body_textbox], append_at_front=True), padding=0)
        self.image_xpath_add_button_4 = MyButton(master=self.finder_image_frame, view='finder', text="Add",
                                                 command=lambda: self.from_textbox_to_textbox(self.finder_image_xpath_4, [self.body_textbox], append_at_front=True), padding=0)

        self.junk_xpath_add_button_1 = MyButton(master=self.finder_junk_frame, view='finder', text="Add",
                                                command=lambda: self.append_junk(self.finder_junk_xpath_1, [self.finder_junk_textbox]), padding=0)
        self.junk_xpath_add_button_2 = MyButton(master=self.finder_junk_frame, view='finder', text="Add",
                                                command=lambda: self.append_junk(self.finder_junk_xpath_2, [self.finder_junk_textbox]), padding=0)
        self.junk_xpath_add_button_3 = MyButton(master=self.finder_junk_frame, view='finder', text="Add",
                                                command=lambda: self.append_junk(self.finder_junk_xpath_3, [self.finder_junk_textbox]), padding=0)
        self.junk_xpath_add_button_4 = MyButton(master=self.finder_junk_frame, view='finder', text="Add",
                                                command=lambda: self.append_junk(self.finder_junk_xpath_4, [self.finder_junk_textbox]), padding=0)
        # Finder RadioButtons
        self.finder_filter = tk.StringVar()
        self.finder_filter_include_radio = MyRadiobutton(master=self.finder_filter_frame, view='finder', text='Include', value='include', variable=self.finder_filter,
                                                         takefocus=False)
        self.finder_filter_remove_radio = MyRadiobutton(master=self.finder_filter_frame, view='finder', text='Remove', value='remove', variable=self.finder_filter, takefocus=False)
        self.finder_filter_remove_radio.invoke()

        # Extractor Frame Lists
        self.view_menu_frame.frame_list = [
            [self.open_extractor_button, self.open_finder_button, self.info_label, self.sync_button, self.refresh_db_button]
        ]
        self.info_frame.frame_list = [
            [self.last_kraken_user_label, self.last_kraken_user_var_label, self.projects_label, self.projects_var_label],
            [self.last_extractor_user_label, self.last_extractor_user_var_label, self.status_label, self.status_var_label, self.botname_label, self.botname_var_label],
            [self.domain_label, self.domain_var_label, self.name_label, self.name_var_label]
        ]
        self.kraken_frame.frame_list = [
            [self.kraken_id_label],
            [self.kraken_textbox, self.kraken_clipboard_button, self.open_source_button, self.load_from_db_button, self.open_items_button]
        ]
        self.json_buttons_frame.frame_list = [
            [self.code_copy_button, self.load_from_existing_button, self.load_without_url_button, self.add_proxy_button],
            [self.allowed_domains_button, self.pubdate_required_button, self.init_wait_button, self.article_wait_button],
            [self.date_order_DMY, self.date_order_MDY, self.date_order_YMD, self.date_order_label]
        ]
        self.json_checkbutton_frame.frame_list = [
            [self.open_source_checkbutton, self.overwrite_domain_checkbutton, self.rdc_checkbutton]
        ]
        self.json_combined_buttons_frame.frame_list = [
            [self.json_buttons_frame],
            [self.json_checkbutton_frame]
        ]
        self.json_full_frame.frame_list = [
            [self.json_label],
            [self.json_textbox, self.json_combined_buttons_frame]
        ]
        self.start_urls_frame.frame_list = [
            [self.start_urls_label],
            [self.start_urls_textbox, self.copy_start_button, self.open_link_button, self.open_domain_button, self.source_name_button, self.source_domain_button]
        ]
        self.menu_frame.frame_list = [
            [self.menu_label],
            [self.menu_textbox, self.copy_menu_button, self.menu_category_button]
        ]
        self.articles_frame.frame_list = [
            [self.articles_label],
            [self.articles_textbox, self.copy_articles_button, self.article_title_button, self.article_recent_button, self.article_cont_href_button, self.article_not_category_button]
        ]
        self.title_frame.frame_list = [
            [self.title_label],
            [self.title_textbox, self.copy_title_button, self.title_h1_button, self.title_single_button]
        ]
        self.pubdate_buttons_frame.frame_list = [
            [self.copy_pubdate_button, self.meta_button, self.standard_regex_button, self.reverse_regex_button, self.word_dot_regex_button],
            [self.word_regex_button, self.blank_regex_button, self.pubdate_replace_button, self.pubdate_copy_without_regex, self.pubdate_single_button]
        ]
        self.pubdate_frame.frame_list = [
            [self.pubdate_label],
            [self.pubdate_textbox, self.pubdate_buttons_frame]
        ]
        self.author_frame.frame_list = [
            [self.author_label],
            [self.author_textbox, self.copy_author_button, self.author_meta_button, self.author_substring_button, self.author_child_text_button, self.author_single_button]
        ]
        self.body_buttons_frame.frame_list = [
            [self.copy_body_button, self.body_not_contains_class_button, self.body_not_contains_desc_class_button,
             self.body_not_contains_id_button, self.body_not_contains_text_button],
            [self.body_not_self_button, self.body_single_button]
        ]
        self.body_frame.frame_list = [
            [self.body_label],
            [self.body_textbox, self.body_buttons_frame]
        ]
        self.sitemap_buttons_frame.frame_list = [
            [self.sitemap_label],
            [self.copy_sitemap_button, self.open_sitemap_button, self.sitemap_xml_button, self.sitemap_html_button]
        ]
        self.sitemap_frame.frame_list = [
            [self.sitemap_label],
            [self.sitemap_textbox, self.sitemap_buttons_frame]
        ]
        self.link_regex_buttons_frame.frame_list = [
            [self.link_regex_label],
            [self.copy_link_regex_button, self.link_regex_button]
        ]
        self.link_regex_frame.frame_list = [
            [self.link_regex_label],
            [self.link_regex_textbox, self.link_regex_buttons_frame]
        ]
        self.bottom_buttons_frame.frame_list = [
            [self.generate_button, self.clear_button]
        ]

        # Finder Frame Lists
        self.finder_filter_frame.frame_list = [
            [self.finder_filter_label, self.finder_filter_include_radio, self.finder_filter_remove_radio]
        ]
        self.article_url_frame.frame_list = [
            [self.finder_article_label, self.finder_article_textbox, self.find_content_button]
        ]
        self.finder_title_frame.frame_list = [
            [self.finder_title_label, self.finder_title_xpath_1, self.title_xpath_select_button_1, self.finder_title_result_1],
            [0, self.finder_title_xpath_2, self.title_xpath_select_button_2, self.finder_title_result_2],
            [0, self.finder_title_xpath_3, self.title_xpath_select_button_3, self.finder_title_result_3],
            [0, self.finder_title_xpath_4, self.title_xpath_select_button_4, self.finder_title_result_4]
        ]
        self.finder_pubdate_frame.frame_list = [
            [self.finder_pubdate_label, self.finder_pubdate_xpath_1, self.pubdate_xpath_select_button_1, self.finder_pubdate_result_1],
            [0, self.finder_pubdate_xpath_2, self.pubdate_xpath_select_button_2, self.finder_pubdate_result_2],
            [0, self.finder_pubdate_xpath_3, self.pubdate_xpath_select_button_3, self.finder_pubdate_result_3],
            [0, self.finder_pubdate_xpath_4, self.pubdate_xpath_select_button_4, self.finder_pubdate_result_4]
        ]
        self.finder_author_frame.frame_list = [
            [self.finder_author_label, self.finder_author_xpath_1, self.author_xpath_select_button_1, self.finder_author_result_1],
            [0, self.finder_author_xpath_2, self.author_xpath_select_button_2, self.finder_author_result_2],
            [0, self.finder_author_xpath_3, self.author_xpath_select_button_3, self.finder_author_result_3],
            [0, self.finder_author_xpath_4, self.author_xpath_select_button_4, self.finder_author_result_4],
        ]
        self.finder_body_frame.frame_list = [
            [self.finder_body_label, self.finder_body_xpath_1, self.body_xpath_select_button_1, self.finder_body_result_1],
            [0, self.finder_body_xpath_2, self.body_xpath_select_button_2, self.finder_body_result_2],
            [0, self.finder_body_xpath_3, self.body_xpath_select_button_3, self.finder_body_result_3],
            [0, self.finder_body_xpath_4, self.body_xpath_select_button_4, self.finder_body_result_4],
        ]
        self.finder_image_frame.frame_list = [
            [self.finder_image_label, self.finder_image_xpath_1, self.image_xpath_add_button_1, self.finder_image_result_1],
            [0, self.finder_image_xpath_2, self.image_xpath_add_button_2, self.finder_image_result_2],
            [0, self.finder_image_xpath_3, self.image_xpath_add_button_3, self.finder_image_result_3],
            [0, self.finder_image_xpath_4, self.image_xpath_add_button_4, self.finder_image_result_4],
        ]
        self.junk_xpath_body_frame.frame_list = [
            [self.junk_body_label, self.finder_junk_textbox, self.find_junk_button, self.add_node_button, self.junk_to_body_button],
            [0, self.junk_body_elements_label]
        ]
        self.finder_junk_frame.frame_list = [
            [self.finder_junk_label, self.finder_junk_xpath_1, self.junk_xpath_add_button_1, self.finder_junk_result_1],
            [0, self.finder_junk_xpath_2, self.junk_xpath_add_button_2, self.finder_junk_result_2],
            [0, self.finder_junk_xpath_3, self.junk_xpath_add_button_3, self.finder_junk_result_3],
            [0, self.finder_junk_xpath_4, self.junk_xpath_add_button_4, self.finder_junk_result_4],
        ]
        if not self.debug_mode:
            dropbox_methods.download_db(config.local_db_path)
        self.create_finder_tables()
        self.update_finder_tables(startup=True)
        self.login()

        self.get_all_widgets(self)
        self.pack_widgets()
        self.window_setup()
        self.bind_all("<Key>", self.on_key_release, "+")
        self.lift()

        webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(config.chrome_path))
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        atexit.register(self.exit_handler)

        t2 = time.time()
        print(f"Booted in {round(t2 - t1, 2)} seconds.")

    def append_junk(self, textbox_from, textboxes_to):
        self.from_textbox_to_textbox(textbox_from, textboxes_to, append=True)
        self.find_junk()

    @staticmethod
    def create_finder_tables():
        con = sqlite3.connect(config.local_db_path)
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS title_xpath (xpath TEXT, count NUMBER)")
        cur.execute("CREATE TABLE IF NOT EXISTS pubdate_xpath (xpath TEXT, count NUMBER)")
        cur.execute("CREATE TABLE IF NOT EXISTS author_xpath (xpath TEXT, count NUMBER)")
        cur.execute("CREATE TABLE IF NOT EXISTS body_xpath (xpath TEXT, count NUMBER)")
        cur.execute("CREATE TABLE IF NOT EXISTS image_xpath (xpath TEXT, count NUMBER)")
        cur.execute("CREATE TABLE IF NOT EXISTS junk (xpath TEXT, count NUMBER)")
        con.commit()
        con.close()

    @staticmethod
    def delete_finder_tables():
        con = sqlite3.connect(config.local_db_path)
        cur = con.cursor()
        cur.execute("DELETE FROM title_xpath")
        cur.execute("DELETE FROM pubdate_xpath")
        cur.execute("DELETE FROM author_xpath")
        cur.execute("DELETE FROM body_xpath")
        cur.execute("DELETE FROM image_xpath")
        cur.execute("DELETE FROM junk")
        con.commit()
        con.close()

    def exit_handler(self):
        self.delete_finder_tables()
        if not self.debug_mode:
            dropbox_methods.merge_and_upload()

    def pack_widgets(self):
        row = 0
        for widget in self.all_widgets:
            if isinstance(widget, MyFrame):
                # Inner Padding exceptions
                if self.generate_button.master == widget:
                    self.pack_frame(widget.frame_list, padx=(2, 315))
                else:
                    self.pack_frame(widget.frame_list)
                if widget in self.winfo_children():
                    widget.grid(row=row, column=0, sticky='W', padx=20, pady=0)
                    row += 1
            if hasattr(widget, 'view') and widget.view != 'extractor' and widget.view != 'menu':
                widget.grid_remove()

    def window_setup(self):
        width = 850
        height = 1080
        starting_height = 0
        if config.side_of_window == "r":
            starting_width = self.winfo_screenwidth() - width - 6
        else:
            starting_width = 0
        self.geometry('%dx%d+%d+%d' % (width, height, starting_width, starting_height))

    def login(self):
        if not os.path.exists('./login_data.py'):
            with open('login_data.py', 'w') as login_file:
                login_file.write('username = "USERNAME_HERE"\npassword = "PASSWORD_HERE"\nuser="Default"\nproxy_username="USERNAME_HERE"\nproxy_password="PASSWORD_HERE"')
                print("Fill in your login details in login_data.py!")
            return

        login_link = "https://dashbeta.aiidatapro.net/"
        try:
            http_proxy = f"http://{login_data.proxy_user}:{login_data.proxy_password}@vpn.aiidatapro.com:3128"
            https_proxy = f"http://{login_data.proxy_user}:{login_data.proxy_password}@vpn.aiidatapro.com:3128"
            proxies = {
                "http": http_proxy,
                "https": https_proxy
            }
            self.session.trust_env = False
            self.session.proxies = proxies
            self.session.auth = HTTPProxyAuth(login_data.proxy_user, login_data.proxy_password)

            self.session.get(login_link, headers=self.headers)
            if 'csrftoken' in self.session.cookies:
                # Django 1.6 and up
                csrftoken = self.session.cookies['csrftoken']
            else:
                csrftoken = self.session.cookies['csrf']
            self.headers['cookie'] = '; '.join([x.name + '=' + x.value for x in self.session.cookies])
            self.headers['content-type'] = 'application/x-www-form-urlencoded'
            payload = {
                'username': login_data.username,
                'password': login_data.password,
                'csrfmiddlewaretoken': csrftoken
            }
            response = self.session.post(login_link, data=payload, headers=self.headers)
            self.headers['cookie'] = '; '.join([x.name + '=' + x.value for x in response.cookies])
        except Exception as e:
            print(e)
            print("Couldn't login")

    def set_word_boundaries(self):
        self.tk.call('tcl_wordBreakAfter', '', 0)
        self.tk.call('set', 'tcl_wordchars', '[a-zA-Z0-9_.-]')
        self.tk.call('set', 'tcl_nonwordchars', '[^a-zA-Z0-9_.-]')

    def get_all_widgets(self, root):
        for widget in root.winfo_children():
            if isinstance(widget, MyText):
                widget['undo'] = True
                widget['bg'] = 'white'
                widget['font'] = self.text_font
            self.all_widgets.append(widget)
            if widget.winfo_children():
                self.get_all_widgets(widget)

    @staticmethod
    def pack_frame(elements, sticky='NW', padx: Union[int, tuple] = 2, pady=2):
        row = 0
        col = 0
        for element_row in elements:
            for element in element_row:
                if element:
                    element.grid(row=row, column=col, sticky=sticky, padx=padx, pady=pady)
                col += 1
            row += 1
            col = 0

    def edit_json(self, initial_key, keyword, value):
        if self.get_strip(self.json_textbox):
            existing_json = json.loads(self.get_strip(self.json_textbox))
            if keyword in existing_json[initial_key].keys():
                if existing_json[initial_key][keyword] == value:
                    del existing_json[initial_key][keyword]
                    self.info_label['text'] = f"{keyword} removed."
                else:
                    existing_json[initial_key][keyword] = value
                    self.info_label['text'] = f"{keyword} set to {value}."
            else:
                existing_json[initial_key][keyword] = value
                self.info_label['text'] = f"{keyword} set to {value}."
            self.json_textbox.delete("1.0", tk.END)
            self.json_textbox.insert("1.0", json.dumps(existing_json, indent=2))
            if keyword == 'date_order':
                self.update_date_order_label()
        else:
            return

    def update_date_order_label(self):
        if self.get_strip(self.json_textbox):
            existing_json = json.loads(self.get_strip(self.json_textbox))
            if 'date_order' in existing_json['scrapy_arguments'].keys():
                self.date_order_label['text'] = existing_json['scrapy_arguments']['date_order']
            else:
                self.date_order_label['text'] = ""

    def copy_code(self, textbox):
        """
        Desc: Function for the button to copy a text fields
        :param textbox: Textbox whose text should be copied to clipboard
        :return:
        """
        value_to_copy = self.get_strip(textbox)
        if value_to_copy:
            pyperclip.copy(value_to_copy)
            self.info_label['text'] = "Value copied."

    def set_kraken_id(self, kraken_id="", unset=False):
        if kraken_id:
            self.kraken_id = kraken_id
            self.title(f"{kraken_id} - {config.window_title}")
        else:
            if not unset and self.get_strip(self.kraken_textbox):
                try:
                    self.kraken_id = re.findall(r'\d+', self.get_strip(self.kraken_textbox))[-1]
                except IndexError:
                    print("No ID found")
                    return
                self.title(f"{self.kraken_id} - {config.window_title}")
            else:
                self.kraken_id = ""
                self.title(config.window_title)

    def color_info_labels(self):
        kraken_text = self.last_kraken_user_var_label['text']
        status_text = self.status_var_label['text']
        botname_text = self.botname_var_label['text']
        domain_text = self.domain_var_label['text']
        name_text = self.name_var_label['text']

        if 'Daniel ' in kraken_text or 'Simeon ' in kraken_text or 'Hristo ' in kraken_text:
            self.last_kraken_user_var_label['foreground'] = 'green'
        elif 'Mihail ' in kraken_text or 'Lilia ' in kraken_text or 'Tsvetan ' in kraken_text:
            self.last_kraken_user_var_label['foreground'] = 'orange'
        elif 'Yasen ' in kraken_text:
            self.last_kraken_user_var_label['foreground'] = 'dark red'
        elif 'Petyo ' in kraken_text:
            self.last_kraken_user_var_label['foreground'] = 'purple'
        else:
            self.last_kraken_user_var_label['foreground'] = 'red'

        if status_text == 'Running':
            self.status_var_label['foreground'] = 'green'
        elif status_text == 'Custom':
            self.status_var_label['foreground'] = 'blue'
        elif status_text == 'Stopped':
            self.status_var_label['foreground'] = 'red'

        if botname_text == 'siteshtml':
            self.botname_var_label['foreground'] = 'green'
        elif botname_text == 'sites_js':
            self.botname_var_label['foreground'] = 'blue'
        elif botname_text == 'feeds':
            self.botname_var_label['foreground'] = 'purple'
        else:
            self.botname_var_label['foreground'] = 'red'

        if domain_text == self.get_domain():
            self.domain_var_label['foreground'] = 'green'
        else:
            self.domain_var_label['foreground'] = 'red'

        if name_text == self.get_source_name(copy=False):
            self.name_var_label['foreground'] = 'green'
        else:
            self.name_var_label['foreground'] = 'red'

    def get_link(self):
        """
        Function to correctly format the Kraken link by searching for the ID in the URL
        :return: The correctly formatted link
        """
        self.set_kraken_id()
        if self.kraken_id:
            link = f"http://kraken.aiidatapro.net/items/edit/{self.kraken_id}/"
            return link
        else:
            return ""

    def open_link_in_browser(self, link):
        webbrowser.get("chrome").open(link)

    def load_from_kraken(self, link, open_source_bool=True):
        """
        Function to fill the extractor with the JSON from Kraken
        :param link: Kraken link / ID
        :param open_source_bool: Bool indicating whether the source link should be opened in a browser tab
        :return:
        """
        self.clear()
        self.kraken_textbox.delete('1.0', tk.END)
        self.kraken_textbox.insert('1.0', link)
        link = self.get_link()  # Format link
        if not link:
            print("No ID found")
            return
        if open_source_bool and self.open_links_check_bool.get():
            self.open_link_in_browser(link)

        # Show correctly formatted link in textbox
        self.kraken_textbox.delete('1.0', tk.END)
        self.kraken_textbox.insert('1.0', link)

        # Show if/who/when edited the source last
        con = sqlite3.connect(config.local_db_path)
        cur = con.cursor()
        cur.execute('SELECT date, user FROM log WHERE id=?', (self.kraken_id,))
        result = cur.fetchone()
        con.close()
        if result:
            self.last_extractor_user_var_label['text'] = f"{result[1]}({result[0][:-3]})"

        items_link = link.replace('/edit', '')
        last_editor_xpath = '//tr[td[child::text()[contains(.,"Updated by")]]]/td[2]//text()'
        last_update_xpath = '//tr[td[child::text()[contains(.,"Last update")]]]/td[2]/text()'
        enabled_xpath = '//tr[td[child::text()[contains(.,"Enabled")]]]/td[2]/i[contains(@class, "true")]'
        active_xpath = '//tr[td[child::text()[contains(.,"Active")]]]/td[2]/i[contains(@class, "true")]'
        botname_xpath = '//tr[td[child::text()[contains(.,"Botname")]]]/td[2]/text()'
        projects_xpath = '//tr[td[child::text()[contains(.,"Projects")]]]/td[2]//li/a/text()'
        name_xpath = '//tr[td[child::text()[contains(.,"Name")]]]/td[2]/text()'
        domain_xpath = '//tr[td[child::text()[contains(.,"URL")]]]/td[2]/a/text()'
        try:
            items_page_response = self.session.get(items_link)
        except Exception:
            print("Couldn't access Kraken")
            return
        tree = html.fromstring(items_page_response.text)
        last_editor = tree.xpath(last_editor_xpath)[1].strip() if len(tree.xpath(last_editor_xpath)) > 2 else "None"
        last_update = tree.xpath(last_update_xpath)[0][:-3]
        enabled = bool(tree.xpath(enabled_xpath))
        active = bool(tree.xpath(active_xpath))
        botname = tree.xpath(botname_xpath)[0]
        projects = tree.xpath(projects_xpath)
        name = tree.xpath(name_xpath)[0]
        domain = tree.xpath(domain_xpath)[0]
        if enabled:
            if active:
                status = "Running"
            else:
                status = "Enabled, but not Active(?)"
        else:
            if active:
                status = "Custom"
            else:
                status = "Stopped"
        self.last_kraken_user_var_label['text'] = f"{last_editor}({last_update})"
        self.status_var_label['text'] = status
        self.projects_var_label['text'] = ','.join(projects)
        self.botname_var_label['text'] = botname
        self.name_var_label['text'] = name
        self.domain_var_label['text'] = domain
        xpath = "//input[@name='feed_properties']/@value"
        link = link.strip()
        kraken_response = self.session.get(link)
        tree = html.fromstring(kraken_response.text)
        code = tree.xpath(xpath)
        code = ''.join(code).replace('\r', '').replace('\n', '')
        try:
            generated_json = json.loads(code)
        except JSONDecodeError:
            # This error indicates the login details are wrong
            print("Incorrect Login Details")
            return
        self.generate(initial_json=generated_json)  # Pass JSON to generate function
        self.info_label["text"] = "Source loaded."

    @staticmethod
    def open_link(link):
        """
        Opens the link given in your browser
        :param link: Link to be opened
        :return:
        """
        if link.strip():
            webbrowser.get("chrome").open(link)

    def load_from_db(self):
        """
        Extracts ID from Kraken Textbox and loads the source from the database
        :return:
        """

        con = sqlite3.connect(config.local_db_path)
        cur = con.cursor()

        if not self.get_strip(self.kraken_textbox):
            return

        kraken_id = re.search(r'\d+', self.get_strip(self.kraken_textbox))
        if kraken_id:
            cur.execute('SELECT * FROM log WHERE id=?', (kraken_id.group(),))
            result = cur.fetchone()
        else:
            cur.execute("SELECT * FROM log WHERE start_urls LIKE '%'||?||'%'", (self.get_strip(self.kraken_textbox),))
            result = cur.fetchone()

        con.close()

        if result:
            self.set_kraken_id(result[0])
            self.last_extractor_user_var_label['text'] = f"{result[-1]}({result[1]})"
            settings = result[10].replace("'", '"').replace("False", '"False"').replace("True",
                                                                                        '"True"')  # Format Bool Values to not crash JSON
            # Create a new var and load database values into it
            json_var = {'scrapy_settings': json.loads(settings), 'scrapy_arguments': {}}
            if result[2]:
                json_var['scrapy_arguments']['start_urls'] = result[2]
            if result[3]:
                json_var['scrapy_arguments']['menu_xpath'] = result[3]
            if result[4]:
                json_var['scrapy_arguments']['articles_xpath'] = result[4]
            if result[5]:
                json_var['scrapy_arguments']['title_xpath'] = result[5]
            if result[6]:
                json_var['scrapy_arguments']['pubdate_xpath'] = result[6]
            if result[7]:
                json_var['scrapy_arguments']['date_order'] = result[7]
            if result[8]:
                json_var['scrapy_arguments']['author_xpath'] = result[8]
            if result[9]:
                json_var['scrapy_arguments']['body_xpath'] = result[9]
            self.domain_var_label['text'] = result[11]
            self.name_var_label['text'] = result[12]
            self.status_var_label['text'] = result[13]
            self.projects_var_label['text'] = result[14]
            self.botname_var_label['text'] = result[15]
            self.generate(initial_json=json_var)
        else:
            self.clear()  # Clear all textboxes to indicate entry doesn't exist

    def open_items_page(self):
        # Function to open the "View Item" page of the source in Kraken
        if self.get_strip(self.kraken_textbox):
            link = self.get_link().replace('/edit', '')
            webbrowser.get("chrome").open(link)
        else:
            return

    def get_source_name(self, copy=True):
        domain = self.get_strip(self.start_urls_textbox)
        if domain and domain[-1] == '/':
            domain = domain[:-1]
        try:
            name = domain.split('//')[1].split('/')[0].replace('www.', '')
            if self.rdc_check_bool.get():
                name += ' - RDC AM'
        except IndexError:
            return
        if name:
            if copy:
                pyperclip.copy(name)
            return name

    def append_textbox_values(self, textbox, before_value="", after_value=""):
        current_value = self.get_strip(textbox)
        textbox.delete("1.0", tk.END)
        textbox.insert("1.0", f'{before_value.strip()}{current_value.strip()}{after_value.strip()}')

    @staticmethod
    def replace_textbox_value(textbox, value):
        textbox.delete("1.0", tk.END)
        textbox.insert("1.0", value)

    def from_textbox_to_textbox(self, textbox_from, textboxes_to, append=False, append_at_front=False, node=''):
        value = self.get_strip(textbox_from)
        if not value:
            return
        if append:
            for textbox in textboxes_to:
                original_value = self.get_strip(textbox)
                textbox.delete('1.0', tk.END)
                textbox.insert('1.0', f"{original_value}{value}")
        elif append_at_front:
            for textbox in textboxes_to:
                original_value = self.get_strip(textbox)
                textbox.delete('1.0', tk.END)
                textbox.insert('1.0', f"{value} | {original_value}")
        else:
            for textbox in textboxes_to:
                textbox.delete('1.0', tk.END)
                textbox.insert('1.0', value+node)
            pyperclip.copy(value+node)

    def open_start_urls_link(self):
        links = self.get_strip(self.start_urls_textbox).split(';')
        if links:
            for link in links:
                link = link.strip()
                link = link if link.endswith('/') else link + '/'
                webbrowser.get("chrome").open(link)

    def open_sitemap_urls_link(self):
        links = self.get_strip(self.sitemap_textbox).split(',')
        if links:
            for link in links:
                link = link.strip()
                # link = link if link.endswith('/') else link + '/'
                webbrowser.get("chrome").open(link)

    def get_domain(self, copy=False):
        link = self.get_strip(self.start_urls_textbox)
        if not link.startswith('http'):
            link = 'http://' + link
        domain = "/".join(link.split(';')[0].split('/')[:3]) + '/'
        if copy:
            pyperclip.copy(domain)
        else:
            return domain

    def find_sitemap(self):
        xpath = "(//*[contains(@href, 'site') or contains(@href, 'Site')][contains(@href, 'map')] | //*[contains(@href, 'map')][contains(@href, 'web')])[1]/@href"
        domain = self.get_domain()
        try:
            sitemap_response = requests.get(domain, headers=self.headers, verify=False)
            tree = html.fromstring(sitemap_response.text)
            sitemap = tree.xpath(xpath)
            if sitemap:
                sitemap_link = sitemap[0]
                if 'http' not in sitemap[0]:
                    if sitemap[0][0] != '/':
                        sitemap[0] = '/' + sitemap[0]
                    sitemap_link = domain[:-1] + sitemap[0]
                webbrowser.get("chrome").open(sitemap_link)
                print(f"Sitemap - {sitemap_link}")
        except Exception as e:
            print(e.args)
            print(f"Site does not load - {domain}")
            return

    def open_domain(self):
        try:
            domain = self.get_domain()
        except IndexError:
            print("Invalid URL")
            return
        try:
            webbrowser.get("chrome").open(domain)
            if self.overwrite_domain_check_bool.get():
                req = requests.get(domain, headers=self.headers, verify=False)
                new_url = req.url
                if new_url[-1] != '/':
                    new_url += '/'
                self.find_sitemap()
                self.replace_textbox_value(self.start_urls_textbox, new_url)
        except Exception:
            print(f"Domain could not load - {domain}")
            return

    def clear(self, skip=None, only=None):
        if skip is None:
            skip = []
        self.set_kraken_id(unset=True)
        if only:
            clearing_set = only
        else:
            clearing_set = self.all_widgets
        for widget in clearing_set:
            if isinstance(widget, MyText) and widget not in skip:
                widget.delete("1.0", tk.END)
        for label in self.var_labels:
            label['text'] = ''

    @staticmethod
    def sort_json(json_object):
        keyorder_arguments = ["start_urls", "menu_xpath", "articles_xpath", "title_xpath", "pubdate_xpath", "date_order",
                              "author_xpath", "body_xpath"]
        sortable_keys = []
        other_keys = []
        for entry in keyorder_arguments:
            if entry in json_object["scrapy_arguments"].keys():
                sortable_keys.append(entry)
        for entry in json_object["scrapy_arguments"].keys():
            if entry not in sortable_keys:
                other_keys.append(entry)
        if 'extractor' in other_keys:
            other_keys.remove('extractor')
        if 'source_id' in other_keys:
            other_keys.remove('source_id')
        sortable_keys.extend(other_keys)
        new_dict = {"scrapy_arguments": {}, "scrapy_settings": {}}
        for entry in sortable_keys:
            new_dict["scrapy_arguments"][entry] = json_object["scrapy_arguments"][entry]
        new_dict["scrapy_settings"] = json_object["scrapy_settings"]
        return new_dict

    def not_empty(self):
        return bool(self.get_strip(self.start_urls_textbox) or
                    self.get_strip(self.menu_textbox) or
                    self.get_strip(self.articles_textbox) or
                    self.get_strip(self.title_textbox) or
                    self.get_strip(self.pubdate_textbox) or
                    self.get_strip(self.author_textbox) or
                    self.get_strip(self.body_textbox))

    def get_text_from_textbox(self, textbox, xpath_name, json_var):
        if self.get_strip(textbox):
            # .replace(re.sub(r'\S\|\S'), ' | ')
            xpath = self.get_strip(textbox).replace('"', "'")
            string_for_remove = ["concat( ' ', ", " ' ' ), concat( ' ', ", ", ' ' )"]
            for s in string_for_remove:
                xpath = xpath.replace(s, '')
            json_var["scrapy_arguments"][xpath_name] = re.sub(r'(\S)\|(\S)', r'\1 | \2', xpath)


        elif xpath_name in json_var["scrapy_arguments"].keys() and self.not_empty():
            json_var["scrapy_arguments"].pop(xpath_name)
        return json_var

    @staticmethod
    def edit_textbox(textbox, xpath_name, json_var):
        textbox.delete("1.0", tk.END)
        if xpath_name in json_var["scrapy_arguments"].keys():
            value = json_var["scrapy_arguments"][xpath_name] or ''
            textbox.insert('1.0', value)

    def default_changes(self, json_var):
        if "link_id_regex" not in json_var["scrapy_arguments"].keys():
            json_var["scrapy_arguments"]["link_id_regex"] = None
        for element in self.xpath_dict.keys():
            self.edit_textbox(self.xpath_dict[element], element, json_var)

        if "sitemap_urls" in json_var["scrapy_arguments"].keys():
            json_var["scrapy_arguments"]["sitemap_urls"] = [sitemap.strip() for sitemap in self.get_strip(self.xpath_dict["sitemap_urls"]).split(',')]

        if "scrapy_settings" in json_var.keys():
            json_var["scrapy_settings"].update(config.settings_json)
        else:
            json_var["scrapy_settings"] = config.settings_json
        return self.sort_json(json_var)

    def fill_code_textbox(self, json_var):
        final_text = json.dumps(json_var, indent=2)
        self.json_textbox.delete("1.0", tk.END)
        self.json_textbox.insert('1.0', final_text)
        return final_text

    def log_code(self, json_dict):
        if self.kraken_id:
            self.log_to_db(json_dict)
        elif self.get_strip(self.kraken_textbox):
            self.set_kraken_id()
            self.log_to_db(json_dict)
        else:
            print("No ID found, logging skipped")

    def log_to_db(self, json_var):
        con = sqlite3.connect(config.local_db_path)
        cur = con.cursor()

        current_time = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
        user = login_data.user if 'user' in dir(login_data) else "Default User"

        start_urls = json_var['scrapy_arguments']['start_urls'] if 'start_urls' in json_var['scrapy_arguments'].keys() else ""
        menu_xpath = json_var['scrapy_arguments']['menu_xpath'] if 'menu_xpath' in json_var['scrapy_arguments'].keys() else ""
        articles_xpath = json_var['scrapy_arguments']['articles_xpath'] if 'articles_xpath' in json_var[
            'scrapy_arguments'].keys() else ""
        title_xpath = json_var['scrapy_arguments']['title_xpath'] if 'title_xpath' in json_var['scrapy_arguments'].keys() else ""
        pubdate_xpath = json_var['scrapy_arguments']['pubdate_xpath'] if 'pubdate_xpath' in json_var['scrapy_arguments'].keys() else ""
        date_order = json_var['scrapy_arguments']['date_order'] if 'date_order' in json_var['scrapy_arguments'].keys() else ""
        author_xpath = json_var['scrapy_arguments']['author_xpath'] if 'author_xpath' in json_var['scrapy_arguments'].keys() else ""
        body_xpath = json_var['scrapy_arguments']['body_xpath'] if 'body_xpath' in json_var['scrapy_arguments'].keys() else ""
        domain = self.domain_var_label['text']
        name = self.name_var_label['text']
        status = self.status_var_label['text']
        projects = self.projects_var_label['text']
        botname = self.botname_var_label['text']

        cur.execute("SELECT id FROM log WHERE id=?", (self.kraken_id,))
        if len(cur.fetchall()):
            print(f"Updated Source {self.kraken_id}")
            cur.execute(
                "UPDATE log SET date=?, start_urls=?, menu_xpath=?, articles_xpath=?, title_xpath=?, pubdate_xpath=?, date_order=?, author_xpath=?, "
                "body_xpath=?, settings=?, domain=?, name=?, status=?, projects=?, botname=?, full_json=?, user=? WHERE id=?",
                (current_time, start_urls, menu_xpath, articles_xpath, title_xpath, pubdate_xpath, date_order, author_xpath, body_xpath,
                 str(json_var['scrapy_settings']), domain, name, status, projects, botname, str(json_var), user, self.kraken_id))
        else:
            print(f"Adding Source {self.kraken_id}")
            cur.execute("INSERT INTO log VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (self.kraken_id, current_time, start_urls, menu_xpath, articles_xpath, title_xpath, pubdate_xpath, date_order, author_xpath,
                         body_xpath,
                         str(json_var['scrapy_settings']), domain, name, status, projects, botname, str(json_var), user))
        con.commit()
        con.close()

    def generate(self, _=None, initial_json=None, load_from_existing_bool=False, leave_current_url=False):
        existing_code = self.get_strip(self.json_textbox)
        if initial_json:
            json_variable = self.default_changes(initial_json)
            self.fill_code_textbox(json_variable)
            self.update_date_order_label()
            for element in self.xpath_dict.keys():
                self.edit_textbox(self.xpath_dict[element], element, json_variable)
            self.color_info_labels()

        elif existing_code:
            try:
                json_variable = json.loads(existing_code)
                if leave_current_url:
                    json_variable['scrapy_arguments']['start_urls'] = self.get_strip(self.start_urls_textbox)
            except JSONDecodeError:
                print("Invalid JSON")
                return
            if not load_from_existing_bool and self.not_empty():
                for element in self.xpath_dict.keys():
                    json_variable = self.get_text_from_textbox(self.xpath_dict[element], element, json_variable)
            json_variable = self.default_changes(json_variable)
            final_json = self.fill_code_textbox(json_variable)
            self.update_date_order_label()
            pyperclip.copy(final_json)
            for element in self.xpath_dict.keys():
                self.edit_textbox(self.xpath_dict[element], element, json_variable)

            self.color_info_labels()
            self.log_code(json_variable)
            self.info_label['text'] = "JSON copied."

        else:
            json_variable = {
                "scrapy_arguments": {
                    "start_urls": "",
                    "articles_xpath": "",
                    "title_xpath": "",
                    "body_xpath": "",
                },
                "scrapy_settings": config.settings_json
            }
            if self.not_empty():
                for element in self.xpath_dict.keys():
                    json_variable = self.get_text_from_textbox(self.xpath_dict[element], element, json_variable)

                json_variable = self.default_changes(json_variable)
                final_json = self.fill_code_textbox(json_variable)
                self.update_date_order_label()
                pyperclip.copy(final_json)
                self.log_code(json_variable)
                self.info_label['text'] = "JSON copied."
            else:
                self.fill_code_textbox(json_variable)

    def fill_found_textboxes(self, tree, column):
        con = sqlite3.connect(config.local_db_path)
        cur = con.cursor()

        if column == 'title_xpath':
            cur.execute("SELECT xpath FROM title_xpath ORDER BY count DESC")
            element = self.finder_title_frame.frame_list

        elif column == 'pubdate_xpath':
            cur.execute("SELECT xpath FROM pubdate_xpath ORDER BY count DESC")
            element = self.finder_pubdate_frame.frame_list

        elif column == 'author_xpath':
            cur.execute("SELECT xpath FROM author_xpath ORDER BY count DESC")
            element = self.finder_author_frame.frame_list

        elif column == 'image_xpath':
            cur.execute("SELECT xpath FROM image_xpath ORDER BY count DESC")
            element = self.finder_image_frame.frame_list
        else:
            cur.execute("SELECT xpath FROM body_xpath ORDER BY count DESC")
            element = self.finder_body_frame.frame_list
        xpath_list = cur.fetchall()
        xpath_list = [x[0] for x in xpath_list]
        con.close()

        final_result = []
        number_of_textboxes = len(self.finder_title_frame.frame_list)
        for xpath in xpath_list:
            try:
                xpath_to_use = xpath if '/@' in xpath or 'text()' in xpath else xpath + '//text()'
                text_results = tree.xpath(xpath_to_use)
                number_of_results = len(tree.xpath(xpath))

                if (column != 'image_xpath' and not text_results) or (self.finder_filter.get() == 'remove' and number_of_results != 1) or number_of_results < 1:
                    continue

                dict_to_append = {'xpath': xpath, 'result': f"({number_of_results}) - {','.join(x.strip() for x in text_results if isinstance(x, str) and x.strip())}"}
                if column == 'image_xpath' or dict_to_append['result'] not in [x['result'] for x in final_result]:
                    final_result.append(dict_to_append)
                    if len(final_result) == number_of_textboxes:
                        break
            except Exception:
                print('broken xpath:', xpath)
        for i, entry in enumerate(final_result):
            element[i][-3].delete('1.0', tk.END)
            element[i][-3].insert('1.0', entry['xpath'])
            element[i][-1].delete('1.0', tk.END)
            element[i][-1].insert('1.0', entry['result'][:50])

    def find_content(self):
        for widget in self.all_widgets:
            if widget.view == 'finder' and isinstance(widget, MyText) and widget.master != self.article_url_frame and widget.master != self.junk_xpath_body_frame \
                    and widget.master != self.finder_junk_frame:
                widget.delete('1.0', tk.END)
        article_url = self.get_strip(self.finder_article_textbox)
        if self.last_tree['link'] == article_url:
            tree = self.last_tree['tree']
        else:
            website_response = requests.get(article_url, headers=self.headers, verify=False)
            website_response.encoding = 'UTF-8'
            tree = html.fromstring(website_response.text)
            self.last_tree['link'] = article_url
            self.last_tree['tree'] = tree
        self.fill_found_textboxes(tree, 'title_xpath')
        self.fill_found_textboxes(tree, 'pubdate_xpath')
        self.fill_found_textboxes(tree, 'author_xpath')
        self.fill_found_textboxes(tree, 'body_xpath')
        self.fill_found_textboxes(tree, 'image_xpath')

    def find_junk(self):
        for frame in self.finder_junk_frame.frame_list:
            for widget in frame:
                if isinstance(widget, MyText):
                    widget.delete('1.0', tk.END)
        body = self.get_strip(self.finder_junk_textbox)
        article_url = self.get_strip(self.finder_article_textbox)
        element = self.finder_junk_frame.frame_list
        if self.last_tree['link'] == article_url:
            tree = self.last_tree['tree']
        else:
            website_response = requests.get(article_url, headers=self.headers, verify=False)
            website_response.encoding = 'UTF-8'
            tree = html.fromstring(website_response.text)
            self.last_tree['link'] = article_url
            self.last_tree['tree'] = tree
        con = sqlite3.connect(config.local_db_path)
        cur = con.cursor()
        results = cur.execute("SELECT xpath FROM junk ORDER BY count DESC").fetchall()
        con.close()
        results = [x[0] for x in results]
        final_result = []
        number_of_textboxes = len(self.finder_junk_frame.frame_list)
        xpath_results = tree.xpath(body)
        xpath_results = [r for r in xpath_results if not isinstance(r, str)]
        usual_number_of_results = len(xpath_results)
        if not usual_number_of_results:
            self.junk_body_elements_label['text'] = "No elements found."
            return
        self.junk_body_elements_label['text'] = f"{usual_number_of_results} elements found."
        for xpath in results:
            new_xpath = body + xpath
            try:
                new_xpath_results = tree.xpath(new_xpath)
                new_xpath_results = [r for r in new_xpath_results if not isinstance(r, str)]
                corrected_number_of_results = len(new_xpath_results)
            except etree.XPathError:
                continue
            if corrected_number_of_results < usual_number_of_results:
                final_result.append([xpath, usual_number_of_results - corrected_number_of_results])
                if len(final_result) == number_of_textboxes:
                    break

        for i, entry in enumerate(final_result):
            element[i][-3].insert('1.0', entry[0])
            element[i][-1].insert('1.0', f'Removes {entry[1]} elements.')

    @staticmethod
    def on_key_release(event):
        ctrl = (event.state & 0x4) != 0
        if event.keycode == 88 and ctrl and event.keysym.lower() != "x":
            event.widget.event_generate("<<Cut>>")

        if event.keycode == 86 and ctrl and event.keysym.lower() != "v":
            event.widget.event_generate("<<Paste>>")

        if event.keycode == 67 and ctrl and event.keysym.lower() != "c":
            event.widget.event_generate("<<Copy>>")

        if event.keycode == 65 and ctrl and event.keysym.lower() != "а":
            event.widget.event_generate("<<SelectAll>>")

    def forget_current_view(self):
        for widget in self.all_widgets:
            if widget.view == self.current_view:
                widget.grid_remove()

    def open_new_view(self, view):
        for widget in self.all_widgets:
            if widget.view == view:
                widget.grid()

    def switch_view(self, view_to_open):
        if view_to_open == self.current_view:
            return
        self.forget_current_view()
        if view_to_open == 'extractor':
            self.open_new_view('extractor')
        elif view_to_open == 'finder':
            self.open_new_view('finder')
        self.current_view = view_to_open

    @staticmethod
    def join_tuple_string(values_tuple) -> str:
        string_list = []
        for element in values_tuple:
            string_list.append(str(element))
        return ', '.join(string_list)

    def extract_xpath_from_regex(self, start_string):
        regex_contains = ['substring', 're:match', 're:replace']
        result = re.match(r"re:match\((.+),\s*'.+',\s*'.+'\)", start_string)
        if result:
            result = result.group(1)
            if not any(s in result for s in regex_contains):
                return result
            else:
                return self.extract_xpath_from_regex(result)

        result = re.match(r"re:replace\((.+),\s*'.+',\s*'.+',\s*'.+'\)", start_string)
        if result:
            result = result.group(1)
            if not any(s in result for s in regex_contains):
                return result
            else:
                return self.extract_xpath_from_regex(result)

        result = re.match(r"substring-.+\((.+),\s*'", start_string)
        if result:
            result = result.group(1)
            if not any(s in result for s in regex_contains):
                return result
            else:
                return self.extract_xpath_from_regex(result)

    def create_dict(self, column, html_tree):
        con = sqlite3.connect(config.local_db_path)
        cur = con.cursor()
        if column == 'title_xpath':
            db_results = cur.execute("SELECT title_xpath FROM log").fetchall()
        elif column == 'pubdate_xpath':
            db_results = cur.execute("SELECT pubdate_xpath FROM log").fetchall()
        elif column == 'author_xpath':
            db_results = cur.execute("SELECT author_xpath FROM log").fetchall()
        else:
            db_results = cur.execute("SELECT body_xpath FROM log").fetchall()
        db_results = [x[0] for x in db_results if x[0]]
        xpath_list = []
        images_list = []
        junk_list = []
        regex_contains = ['substring', 're:match', 're:replace']
        image_contains = ['img', 'image', 'featured', 'thumb', 'figure']
        body_contains = ['/text()', "'row'", '::img', '//article/', '//main/', 'figcaption', "//div[contains(@class,'-content')]", '//section/',
                         "//div[contains(@class,'content')]", '@src', 'string(']
        date_contains = "//meta[contains(@*, 'time')]"
        for xpath in db_results:
            if column == 'pubdate_xpath' and date_contains in xpath:
                continue

            # Removes (xpath | xpath)[1] issues
            if '|' in xpath and xpath.startswith('(') and xpath.endswith(')[1]'):
                xpath = xpath[1:-4]

            if "' | '" not in xpath:
                split_xpath_list = xpath.split('|')
            else:
                split_xpath_list = [xpath]

            for updated_xpath in split_xpath_list:
                # Remove spaces from contains
                updated_xpath = re.sub(r"contains\(@(\w+),\s+'([^']+)'", r"contains(@\g<1>,'\g<2>'", updated_xpath).strip()

                if any(s in updated_xpath for s in regex_contains):
                    updated_xpath = self.extract_xpath_from_regex(updated_xpath)
                    if not updated_xpath:
                        continue

                if column == 'body_xpath':
                    if any(s in updated_xpath for s in body_contains):
                        continue

                    else:
                        if updated_xpath.endswith('/p'):
                            updated_xpath = updated_xpath[:-2]

                        if '/node()' in updated_xpath:
                            body_and_junk = updated_xpath.split('/node()')
                            updated_xpath = body_and_junk[0]
                            junk_list.append(body_and_junk[1])

                        if any(s in updated_xpath for s in image_contains):
                            images_list.append(updated_xpath)
                            continue

                        while updated_xpath and updated_xpath[-1] == '/':
                            updated_xpath = updated_xpath[:-1]

                if '@' not in updated_xpath and updated_xpath.count('/') < 3:
                    continue

                xpath_list.append(updated_xpath.strip())

        list_to_remove = []
        for xpath in xpath_list:
            try:
                html_tree.xpath(xpath)
            except etree.XPathError:
                list_to_remove.append(xpath)

        xpath_list = [x for x in xpath_list if x not in list_to_remove]

        if column == 'body_xpath':
            list_to_remove = []
            for xpath in images_list:
                try:
                    html_tree.xpath(xpath)
                except etree.XPathError:
                    list_to_remove.append(xpath)

            images_list = [x for x in images_list if x not in list_to_remove and ' or ' not in x and ' and ' not in x]
            images_dict = dict()
            for x in images_list:
                images_dict[x] = images_dict.get(x, 0) + 1
            results = sorted(images_dict.items(), key=lambda d: d[1], reverse=True)
            for entry in results:
                cur.execute("INSERT INTO image_xpath VALUES (?, ?)", (entry[0], entry[1]))

            revised_junk_list = []
            bad_junk_indicators = [' or ', ' and ', '//', 'position', 'self::div']
            for item in junk_list:
                if not item:
                    continue
                item = item.replace('] [not', '][not')
                items = item.split('][not')
                for split_item in items:
                    if not split_item.startswith('[not'):
                        split_item = '[not' + split_item
                    if not split_item.endswith(']'):
                        split_item += ']'
                    if any(s in split_item for s in bad_junk_indicators) or ('contains' not in item or 'self' not in item):
                        continue
                    revised_junk_list.append(split_item)

            junk_dict = dict()
            for x in revised_junk_list:
                junk_dict[x] = junk_dict.get(x, 0) + 1
            results = sorted(junk_dict.items(), key=lambda d: d[1], reverse=True)
            for entry in results:
                cur.execute("INSERT INTO junk VALUES (?, ?)", (entry[0], entry[1]))

        created_dict = dict()
        for x in xpath_list:
            created_dict[x] = created_dict.get(x, 0) + 1

        results = sorted(created_dict.items(), key=lambda d: d[1], reverse=True)

        if column == 'title_xpath':
            for entry in results:
                cur.execute("INSERT INTO title_xpath VALUES (?, ?)", (entry[0], entry[1]))
        elif column == 'pubdate_xpath':
            for entry in results:
                cur.execute("INSERT INTO pubdate_xpath VALUES (?, ?)", (entry[0], entry[1]))
        elif column == 'author_xpath':
            for entry in results:
                cur.execute("INSERT INTO author_xpath VALUES (?, ?)", (entry[0], entry[1]))
        elif column == 'body_xpath':
            for entry in results:
                cur.execute("INSERT INTO body_xpath VALUES (?, ?)", (entry[0], entry[1]))

        con.commit()
        con.close()

    def update_finder_tables(self, startup=False):
        if startup:
            con = sqlite3.connect(config.local_db_path)
            cur = con.cursor()
            cur.execute("SELECT id FROM log")
            print(f"Hello, {login_data.user}")
            print(f"The database contains {len(cur.fetchall())} entries.")
            con.close()
        else:
            self.delete_finder_tables()

        website_response = requests.get('http://example.python-scraping.com/places/default/index/0', verify=False)
        tree = html.fromstring(website_response.text.encode())

        self.create_dict('title_xpath', html_tree=tree)
        self.create_dict('pubdate_xpath', html_tree=tree)
        self.create_dict('author_xpath', html_tree=tree)
        self.create_dict('body_xpath', html_tree=tree)

        if not startup:
            self.info_label['text'] = "Tables refreshed."

    @staticmethod
    def get_strip(widget):
        return widget.get('1.0', 'end-1c').strip().replace('\n', '')

if __name__ == '__main__':
    app = MainApplication()
    app.mainloop()
