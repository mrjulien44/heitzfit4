import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN

class Heitzfit4ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Heitzfit4."""

    VERSION = 2

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title="Heitzfit4", data=user_input)
            #return self.async_show_form(step_id="user", data_schema=user_form)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("club"): str,
                vol.Required("username"): str,
                vol.Required("password"): str,
                vol.Required("nbdays", default=8): cv.positive_int
            })
        )

    @staticmethod
    @callback
    # def async_get_options_flow(config_entry):
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return Heitzfit4OptionsFlowHandler(config_entry)
        # return OptionsFlowHandler()


class Heitzfit4OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Heitzfit4 options."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("club", default=self.config_entry.data.get("club")): str,
                vol.Required("username", default=self.config_entry.data.get("username")): str,
                vol.Required("password", default=self.config_entry.data.get("password")): str,
                vol.Required("nbdays", default=self.config_entry.data.get("nbdays")): str,
            })
        )

# class OptionsFlowHandler():
#     """Handle Heitzfit4 options."""

#     # def __init__(self, config_entry):
#     #     self.config_entry = config_entry
#     @property
#     def config_entry(self):
#         return self.hass.config_entries.async_get_entry(self.handler)

#     async def async_step_init(self, user_input=None):
#         """Manage the options."""
#         if user_input is not None:
#             return self.async_create_entry(title="", data=user_input)

#         return self.async_show_form(
#             step_id="init",
#             data_schema=vol.Schema({
#                 vol.Required("club", default=self.config_entry.data.get("club")): str,
#                 vol.Required("username", default=self.config_entry.data.get("username")): str,
#                 vol.Required("password", default=self.config_entry.data.get("password")): str,
#                 vol.Required("nbdays", default=self.config_entry.data.get("nbdays")): str,
#             })
#         )