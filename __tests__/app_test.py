from flashcards import addCards
import pytest

def test_addCards():
    assert addCards("test", "test", "test", "test") == "test"

