"""
Wonderland Adventure
_____________________
A platforming game where the goal is to
collect as many coins as possible.  The player
must collect coins while avoiding enemies and trying
not to fall into any pits.
_____________________
COM 302 Final Game Project
Ashley Fredricksen
Kanokwan Budsarakoon
Due Date: 12/11/2020
"""
import arcade

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Wonderland Adventure!"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 1
TILE_SCALING = 0.5
COIN_SCALING = 0.5
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * TILE_SCALING)

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 10
GRAVITY = 1
PLAYER_JUMP_SPEED = 20

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
LEFT_VIEWPORT_MARGIN = 200
RIGHT_VIEWPORT_MARGIN = 200
BOTTOM_VIEWPORT_MARGIN = 150
TOP_VIEWPORT_MARGIN = 100

PLAYER_START_X = 64
PLAYER_START_Y = 225


class StartScreen(arcade.View):
    """ Class that shows the screen upon startup of the game """

    def __init__(self):
        super().__init__()
        self.texture = arcade.load_texture("images/screen/start_screen.png")

    def on_show(self):
        # reset the viewport
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

    def on_draw(self):
        # draws the start screen
        arcade.start_render()
        self.texture.draw_sized(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT)

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        # starts the game after the mouse is pressed
        game_view = MyGame()
        game_view.setup(game_view.level)
        self.window.show_view(game_view)


class GameOver(arcade.View):
    """ Class that displays the game over screen """

    def __init__(self):
        super().__init__()
        self.texture = arcade.load_texture("images/screen/game_over.png")

    def on_show(self):
        # reset the viewport
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

    def on_draw(self):
        # draws the game over screen
        arcade.start_render()
        self.texture.draw_sized(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT)

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        # when mouse is pressed, game restarts
        game_view = MyGame()
        game_view.setup(game_view.level)
        self.window.show_view(game_view)


class MyGame(arcade.View):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        # super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        super().__init__()

        # These are 'lists' that keep track of our sprites. Each sprite should
        # go into a list.
        self.coin_list = None
        self.wall_list = None
        self.foreground_list = None
        self.background_list = None
        self.dont_touch_list = None
        self.player_list = None

        # Separate variable that holds the player sprite
        self.player_sprite = None

        # Our physics engine
        self.physics_engine = None

        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        # keep track of coins collected/score and lives
        self.score = 0
        self.lives = 5

        # Where is the right edge of the map?
        self.end_of_map = 0

        # Level
        self.level = 1

        # Load sounds
        self.collect_coin_sound = arcade.load_sound("sounds/coin1.wav")
        self.jump_sound = arcade.load_sound("sounds/jump1.wav")
        self.game_over = arcade.load_sound("sounds/lose2.wav")

    def setup(self, level):
        """ Set up the game here. Call this function to restart the game. """

        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        # Keep track of the score
        self.score = 0

        # Keep track of lives
        # self.lives = 5

        # Create the Sprite lists
        self.player_list = arcade.SpriteList()
        self.foreground_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()

        # Set up the player, specifically placing it at these coordinates.
        image_source = "images/Alice/Alice7_front.png"
        self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y
        self.player_list.append(self.player_sprite)

        # --- Load in a map from the tiled editor ---

        # Name of the layer in the file that has our platforms/walls
        platforms_layer_name = 'Platforms'
        moving_platforms_layer_name = 'Moving Platforms'
        # Name of the layer that has items for pick-up
        coins_layer_name = 'Coins'
        # Name of the layer that has items for foreground
        foreground_layer_name = 'Foreground'
        # Name of the layer that has items for background
        background_layer_name = 'Background'
        # Name of the layer that has items we shouldn't touch
        dont_touch_layer_name = "Don't Touch"

        # Map name
        map_name = f"map4_level_{level}.tmx"

        # Read in the tiled map
        my_map = arcade.tilemap.read_tmx(map_name)

        # Calculate the right edge of the my_map in pixels
        self.end_of_map = my_map.map_size.width * GRID_PIXEL_SIZE

        # -- Background
        self.background_list = arcade.tilemap.process_layer(my_map,
                                                            background_layer_name,
                                                            TILE_SCALING)

        # -- Foreground
        self.foreground_list = arcade.tilemap.process_layer(my_map,
                                                            foreground_layer_name,
                                                            TILE_SCALING)

        # -- Platforms
        self.wall_list = arcade.tilemap.process_layer(map_object=my_map,
                                                      layer_name=platforms_layer_name,
                                                      scaling=TILE_SCALING,
                                                      use_spatial_hash=True)
        # -- Moving Platforms
        moving_platforms_list = arcade.tilemap.process_layer(my_map, moving_platforms_layer_name, TILE_SCALING)
        for sprite in moving_platforms_list:
            self.wall_list.append(sprite)

        # -- Coins
        self.coin_list = arcade.tilemap.process_layer(my_map,
                                                      coins_layer_name,
                                                      TILE_SCALING,
                                                      use_spatial_hash=True)

        # -- Don't Touch Layer
        self.dont_touch_list = arcade.tilemap.process_layer(my_map,
                                                            dont_touch_layer_name,
                                                            TILE_SCALING,
                                                            use_spatial_hash=True)

        # --- Other stuff
        # Set the background color
        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)

        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.wall_list,
                                                             GRAVITY)

    def on_draw(self):
        """ Render the screen. """

        # Clear the screen to the background color
        arcade.start_render()

        # Draw our sprites
        self.wall_list.draw()
        self.background_list.draw()
        # self.wall_list.draw()
        self.coin_list.draw()
        self.dont_touch_list.draw()
        self.player_list.draw()
        self.foreground_list.draw()

        # Draw our score on the screen, scrolling it with the viewport
        score_text = f"Coins: {self.score}"
        arcade.draw_text(score_text, 20 + self.view_left, 600 + self.view_bottom,
                         arcade.csscolor.BLACK, 18)

        # draw life count and keep it on screen during scroll
        # life_text = f"Lives: {self.lives}"
        # arcade.draw_text(life_text, 20 + self.view_left, 560 + self.view_bottom, arcade.csscolor.BLACK, 18)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP or key == arcade.key.W or key == arcade.key.SPACE:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                arcade.play_sound(self.jump_sound)
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0

    def update(self, delta_time):
        """ Movement and game logic """

        # Move the player with the physics engine
        self.physics_engine.update()

        # Update animations
        self.coin_list.update_animation(delta_time)
        self.background_list.update_animation(delta_time)

        # Update walls, used with moving platforms
        self.wall_list.update()

        # See if the wall hit a boundary and needs to reverse direction.
        for wall in self.wall_list:

            if wall.boundary_right and wall.right > wall.boundary_right and wall.change_x > 0:
                wall.change_x *= -1
            if wall.boundary_left and wall.left < wall.boundary_left and wall.change_x < 0:
                wall.change_x *= -1
            if wall.boundary_top and wall.top > wall.boundary_top and wall.change_y > 0:
                wall.change_y *= -1
            if wall.boundary_bottom and wall.bottom < wall.boundary_bottom and wall.change_y < 0:
                wall.change_y *= -1

        # See if we hit any coins
        coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                             self.coin_list)

        # Loop through each coin we hit (if any) and remove it
        for coin in coin_hit_list:
            # Remove the coin
            coin.remove_from_sprite_lists()
            # Play a sound
            arcade.play_sound(self.collect_coin_sound)
            # Add one to the score
            self.score += 1

        # Track if we need to change the viewport
        changed_viewport = False

        # Did the player fall off the map?
        if self.player_sprite.center_y < -100:
            self.lives -= 1
            self.player_sprite.change_x = 0
            self.player_sprite.change_y = 0
            self.player_sprite.center_x = PLAYER_START_X
            self.player_sprite.center_y = PLAYER_START_Y

            # Set the camera to the start
            self.view_left = 0
            self.view_bottom = 0
            changed_viewport = True
            arcade.play_sound(self.game_over)
            # ends the game if the player runs out of lives
            # if self.lives == 0:
            #     view = GameOver()
            #     self.window.show_view(view)
            #     arcade.run()

        # Did the player touch something they should not?
        if arcade.check_for_collision_with_list(self.player_sprite,
                                                self.dont_touch_list):
            self.lives -= 1
            self.player_sprite.change_x = 0
            self.player_sprite.change_y = 0
            self.player_sprite.center_x = PLAYER_START_X
            self.player_sprite.center_y = PLAYER_START_Y

            # Set the camera to the start
            self.view_left = 0
            self.view_bottom = 0
            changed_viewport = True
            arcade.play_sound(self.game_over)
            # ends the game if the player runs out of lives
            # if self.lives == 0:
            #     view = GameOver()
            #     self.window.show_view(view)
            #     arcade.run()

        # See if the user got to the end of the level
        if self.player_sprite.center_x >= self.end_of_map:
            # Advance to the next level
            self.level += 1

            # Load the next level
            self.setup(self.level)

            # Set the camera to the start
            self.view_left = 0
            self.view_bottom = 0
            changed_viewport = True

        # --- Manage Scrolling ---

        # Scroll left
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed_viewport = True

        # Scroll right
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            changed_viewport = True

        # Scroll up
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary
            changed_viewport = True

        # Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            changed_viewport = True

        if changed_viewport:
            # Only scroll to integers. Otherwise we end up with pixels that
            # don't line up on the screen
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            # Do the scrolling
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)


def main():
    """ Main method """
    #
    # window = MyGame()
    # window.setup(window.level)
    # arcade.run()

    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = StartScreen()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
