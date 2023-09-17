"""Text for bot messages, commands."""

# Messages:
start_choose_role = "Choose your role"

after_login = "Hello {full_name} your role is {role}"

display_user_menu = "Main menu ({full_name}: {role}):"

display_add_shop = "Add shop by API key"

display_unlink_shop = "Unlink shop from the seller."

unlink_shop = "Forget shop {name}?"

display_shop_list = "Available shops:"

display_shop_menu = "Shop: `{shop_name}`"

display_shop_info = \
    "<b>Full shop information</b>\n" \
    "Id: {id}\n" \
    "Name: {name}\n" \
    "Slug: {slug}\n" \
    "API key: {api_key}\n" \
    "Vendor Name: {vendor_name}\n" \
    "Is Active: {is_active}\n" \
    "Stop updated price: {stop_updated_price}\n" \
    "Individual updating time: {individual_updating_time}\n"

activate_shop = "Shop name: {name}\nIs active: {is_active}"

price_updating = "Shop name: {name}\n" \
                 "Price updating: {switch}"

display_ban = "You are banned."

display_not_active = "Your account is not active."


ask_username = "Type your Username:"

ask_password = "Type password:"

password_received = "Password received: {password} \nPlease wait."

logged_in_as_admin = "You are logged in as admin."

wrong_credentials = "Wrong username or password.\nDo you want to try again?"

ask_shop_api_key = "Type API key of your shop:"

api_key_received = "API key received: {shop_api_key} \nPlease wait."

logged_in_as_seller = "You are logged in as Seller."

wrong_api_key = "Wrong API key, please enter it again:"


# Commands:
start_command_description = "Start"
menu_command_description = "Available actions"
cancel_command_description = "Cancel the current operation"
sign_out_command_description = "logout TEST command"
