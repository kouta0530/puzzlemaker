from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from puzzle.tests.helper import make_Puzzles


class IntegrationTest(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument("--headless")
        options.add_argument("--disable-dev-shm-usage")
        cls.host = 'web'
        cls.selenium = webdriver.Remote(
            command_executor='http://selenium:4444/wd/hub',
            desired_capabilities=DesiredCapabilities.CHROME,
            options=options
        )
        cls.selenium.implicitly_wait(5)
        super(IntegrationTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(IntegrationTest, cls).tearDownClass()

    def test_title_logo_url(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        url = self.selenium.find_element_by_tag_name('a').get_attribute('href')
        self.assertEquals(url, self.live_server_url + '/')

    def test_msg_no_posted_puzzle(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        msg = self.selenium.find_element_by_class_name(
            'no-puzzle-data-msg').text
        self.assertEquals(msg, 'パズルが投稿されていません')

    def test_posted_puzzle(self):
        make_Puzzles(1)
        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        msg = self.selenium.find_elements_by_class_name(
            'no-puzzle-data-msg')
        self.assertEquals(msg, [])

        puzzle = self.selenium.find_element_by_class_name('puzzle')
        puzzle_title = puzzle.find_element_by_tag_name('h3')
        puzzle_imgs = puzzle.find_elements_by_tag_name('img')

        self.assertEquals(puzzle_title.text, 'test1')
        self.assertEquals(len(puzzle_imgs), 2)
        self.assertEquals(
            puzzle_imgs[0].get_attribute('src'),
            self.live_server_url + '/static/img/no_image.png')
        self.assertEquals(puzzle_imgs[1].get_attribute('alt'), '投稿者アイコン')

    def test_scroll_load_puzzles(self):
        make_Puzzles(40)
        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        puzzles = self.selenium.find_elements_by_class_name('puzzle')
        self.assertEquals(len(puzzles), 30)
        self.selenium.execute_script(
            "window.scrollTo(0, document.body.clientHeight);")

        puzzles = self.selenium.find_elements_by_class_name('puzzle')