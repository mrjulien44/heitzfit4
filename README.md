# heitzfit4 integration for Home Assistant
![heitzfit4 logo](doc/logo_heitzfit4.png)
## Installation

### Using HACS

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=mrjulien44&repository=heitzfit4&category=integration)

OR

If you can't find the integration, add this repository to HACS, then:  
HACS > Integrations > **heitzfit4**

### Manual install

Copy the `heitzfit4` folder from latest release to the `custom_components` folder in your `config` folder.

## Goal

The heitzfit4 integration is used to get your planning and booked activities from your sport center
.
## Configuration

Click on the following button:  
[![Open your Home Assistant instance and start setting up a new integration of a specific brand.](https://my.home-assistant.io/badges/brand.svg)](https://my.home-assistant.io/redirect/brand/?brand=heitzfit4)  

Or go to :  
Settings > Devices & Sevices > Integrations > Add Integration, and search for "heitzfit4"

You can choose between two options when adding a config entry.  

### using 4 parameters : id of your club, username, password and number of days for planning

Use your heitzfit4 with username, password and Club Id:  
![heitzfit4 config flow](doc/config_flow_username_password.png)

## Usage


| Sensor | Description |
|--------|-------------|
| `sensor.heitzfit4_planning` | Planning for coming days |


The sensors are updated every 120 minutes.

## Cards

Use a markdown card for now

Sample for planning :

```
type: markdown
content: >-
  <h2><img src = '/local/images/logo_globalfit.png' alt='GlobalFit Club'
  align='middle' height='50px'> Planning</h2> {%- set days =
  state_attr('sensor.heitzfit4_planning', 'planning') -%} {%- for day in days
  -%}
    <h2><ha-icon icon="mdi:calendar-today"></ha-icon> {{as_timestamp(day) | timestamp_custom('%d %b') + ' (' + as_timestamp(day) | timestamp_custom('%A') + ')'}}</h2>
    {%- for activities in days[day] -%}
      {%- if activities.deleted == False%}
        {%- if activities.placesTaken | int == activities.placesMax | int -%}
          {%- set places = "<font color='#c83110'>(" + activities.placesTaken | string + "/" + activities.placesMax | string + ")</font>" -%}
        {%- else -%}
          {%- set places = "(" + activities.placesTaken | string + "/" + activities.placesMax | string + ")"-%}
        {%- endif -%}
        {%- set booking = "info" -%}
        {%- if activities.booked %}
          {%- set booking = "success" -%}
        {%- endif -%}
          <ha-alert title="{{as_timestamp(activities.start) | timestamp_custom('%R') + '&nbsp;&nbsp;' + activities.activity}}" alert-type="{{booking}}">
            {{'&nbsp;&nbsp;&nbsp;@&nbsp;' + activities.room + '&nbsp;&nbsp;&nbsp;&nbsp;' + places}}
            
            {# --- BOUTON DE RÉSERVATION (VIA SCRIPT AUTOMATISÉ) --- #}
            {%- if not activities.booked and (activities.placesTaken | int < activities.placesMax | int) %}
              <div style="text-align: right; margin-top: -22px; position: relative; z-index: 2;">
                <a href="/api/services/script/heitzfit_reserver_action?activity_id={{ activities.id }}" 
                   style="background-color: #2196F3; color: white; padding: 4px 8px; text-decoration: none; border-radius: 4px; font-weight: bold; font-size: 0.85em; display: inline-block;">
                   ➕ Réserver
                </a>
              </div>
            {%- endif -%}
            
            {# --- BOUTON D'ANNULATION (VIA SCRIPT AUTOMATISÉ) --- #}
            {%- if activities.booked %}
              <div style="text-align: right; margin-top: -22px; position: relative; z-index: 2;">
                <a href="/api/services/script/heitzfit_annuler_action?activity_id={{ activities.id }}" 
                   style="background-color: #f44336; color: white; padding: 4px 8px; text-decoration: none; border-radius: 4px; font-weight: bold; font-size: 0.85em; display: inline-block;">
                   ➖ Annuler
                </a>
              </div>
            {%- endif -%}
            
          </ha-alert>
      {%- endif -%}
    {%- endfor -%}
  {%- endfor -%}

```
![heitzfit4 planning detail](doc/planning.png)

Sample for booking :

```
{%- set days = state_attr('sensor.heitzfit4_planning', 'planning') -%} {%- for day in days -%}
  <h2><ha-icon icon="mdi:calendar-today"></ha-icon> {{as_timestamp(day) | timestamp_custom('%d %b')}}{{' (' + as_timestamp(day) | timestamp_custom('%A') + ')'}}</h2>
  {%- for activities in days[day] -%}
    {%- set places = activities.placesTaken | string + "/" + activities.placesMax | string -%}
    {%- set booking = "info" -%}
    {%- if activities.booked %}
      {%- set booking = "success" -%}
      <ha-alert title="{{as_timestamp(activities.start) | timestamp_custom('%R') + '&nbsp;&nbsp;' + activities.activity + '&nbsp;&nbsp;(' + places + ')'}}" alert-type="{{booking}}">{{'&nbsp;&nbsp;&nbsp;@&nbsp;' + activities.room}}</ha-alert>
    {%- endif -%}
  {%- endfor -%}
{%- endfor -%}
```
![heitzfit4 booking detail](doc/bookings.png)

## script pour pouvoir réserver et annuler
```
heitzfit_reserver_action:
  alias: "Heitzfit - Réserver et Actualiser"
  mode: parallel
  fields:
    activity_id:
      description: "L'identifiant de l'activité à réserver"
      example: "104434280"
  sequence:
    - action: rest_command.heitzfit_book
      data:
        activity_id: "{{ activity_id }}"
    - delay: "00:00:01" # Léger délai pour laisser à l'API Heitzfit le temps de traiter la demande
    - action: homeassistant.update_entity
      target:
        entity_id: sensor.heitzfit4_planning
    - action: browser_mod.window_reload # <--- AJOUT ICI : Force la page web à s'actualiser d'elle-même
      data: {}
 
heitzfit_annuler_action:
  alias: "Heitzfit - Annuler et Actualiser"
  mode: parallel
  fields:
    activity_id:
      description: "L'identifiant de l'activité à annuler"
      example: "104434280"
  sequence:
    - action: rest_command.heitzfit_book_delete
      data:
        activity_id: "{{ activity_id }}"
    - delay: "00:00:01"
    - action: homeassistant.update_entity
      target:
        entity_id: sensor.heitzfit4_planning
    - action: browser_mod.window_reload # <--- AJOUT ICI : Force la page web à s'actualiser d'elle-même
      data: {}
```

## Calendar

Show your bookings in a dedicated calendar
![heitzfit4 calendar view](doc/calendar.png)

## Removing the integration

This integration follows standard integration removal. No extra steps are required.