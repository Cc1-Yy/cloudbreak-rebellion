class GameState:
    """
    Base class for game states. Provides interface for entering, exiting,
    handling events, updating logic, and drawing to the screen.
    """

    def __init__(self, game):
        """
        Store reference to the main Game object for access to shared resources.
        """
        self.game = game

    def enter(self):
        """
        Called when the state is pushed or activated.
        Override to initialize state-specific resources.
        """
        pass

    def exit(self):
        """
        Called when the state is popped or deactivated.
        Override to clean up state-specific resources.
        """
        pass

    def handle_event(self, event):
        """
        Handle a single Pygame event.
        Override to respond to input (keyboard, mouse, etc.).
        """
        pass

    def update(self, dt):
        """
        Update game logic.
        dt: Delta time in seconds since the last update call.
        """
        pass

    def draw(self, screen):
        """
        Render content to the given screen surface.
        screen: The Pygame display surface.
        """
        pass
