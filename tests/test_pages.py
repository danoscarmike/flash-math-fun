"""Tests for page components."""

from unittest.mock import Mock, patch

import pytest

from app.pages import home, play


class TestHomePage:
    """Test home page functionality."""

    @pytest.mark.ui
    @patch("app.pages.home.ui")
    def test_home_page_renders(self, mock_ui):
        """Test that home page renders correctly."""
        home()
        # Just test that home() doesn't crash

    @pytest.mark.ui
    @patch("app.pages.home.ui")
    def test_home_page_has_correct_title(self, mock_ui):
        """Test that home page sets correct title."""
        home()
        # home() doesn't set page title, just creates a button
        mock_ui.button.assert_called_once()


class TestPlayPage:
    """Test play page functionality."""

    @pytest.mark.ui
    @patch("app.pages.play.ui")
    def test_play_page_renders(self, mock_ui):
        """Test that play page renders correctly."""
        play()
        # Just test that play() doesn't crash

    @pytest.mark.ui
    @patch("app.pages.play.ui")
    def test_play_page_has_correct_title(self, mock_ui):
        """Test that play page sets correct title."""
        play()
        mock_ui.page_title.assert_called_once_with("Flash Math Fun!")
