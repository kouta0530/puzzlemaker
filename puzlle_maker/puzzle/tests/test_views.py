from django.test import TestCase, Client
from django.urls import reverse
from puzzle.models import Puzzle
from django.utils import timezone


class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        for i in range(62):
            self.puzzle = Puzzle.objects.create(
                title="test" + str(i),
                size=2,
                created_at=timezone.now(),
                update_at=timezone.now(),
                picture_url="test.png",
                user_id="abdg3fh"
            )

    def test_get_index_page(self):
        response = self.client.get('')
        self.assertEquals(response.status_code, 200)
        compared_data = list(Puzzle.objects.all().values())[:30]
        self.assertEquals(response.context['puzzle'], compared_data)

    def test_get_additional_puzzle_data(self):
        url = reverse('get puzzle data', kwargs={'id': 1})
        response = self.client.get(url)
        additional_puzzles = response.json()
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(additional_puzzles), 30)
        self.assertEquals(additional_puzzles[0]['title'], 'test30')
        self.assertEquals(additional_puzzles[-1]['title'], 'test59')

    def test_can_not_be_acquired_30_pieces_of_data(self):
        url = reverse('get puzzle data', kwargs={'id': 2})
        response = self.client.get(url)
        additional_puzzles = response.json()
        self.assertEquals(len(additional_puzzles), 2)

    def test_search_for_word_equals_title_puzzle_data(self):
        response = self.client.get('/puzzles/?search_words=test')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['puzzle'],
                          list(Puzzle.objects.all().values())[:30])

        response = self.client.get('/puzzles/?search_words=test&id=2')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['puzzle'],
                          list(Puzzle.objects.all().values())[30:60])

        response = self.client.get('/puzzles/?search_words=test&id=3')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['puzzle'],
                          list(Puzzle.objects.all().values())[60:62])

    def test_search_by_multiple_words(self):
        Puzzle.objects.create(title="cat",
                              size=2,
                              created_at=timezone.now(),
                              update_at=timezone.now(),
                              picture_url="test.png",
                              user_id="abdg3fh")
        response = self.client.get("/puzzles/?search_words=test1 cat")
        self.assertEquals(len(response.context['puzzle']), 12)

    def test_search_with_blanks(self):
        response = self.client.get('/puzzles/')
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, '/')

    def test_no_work_that_matches_the_search_results(self):
        response = self.client.get('/puzzles/?search_words=aaaaaaaa&id=1')
        self.assertIn("パズルが投稿されていません", response.content.decode())
