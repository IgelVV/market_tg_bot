## Conversation handler flow:

* /start (check if authenticated: skip roles and auth)
* CHOOSE_ROLE (admin/user)
  * admin - LOGG_IN -> PASSWORD -> SHOP_LIST
  * user - check confirmation by admin: 
    * if not confirmed: API_KEY -> WAITING -> END
    * else: SHOP_MENU
* SHOP_LIST (for admins)
* SHOP_MENU
  * SHOP_INFO
  * ACTIVATE
  * PRICE_UPDATING