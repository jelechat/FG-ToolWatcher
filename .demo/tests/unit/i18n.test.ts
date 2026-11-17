import { describe, expect, it } from 'vitest'
import en from '../../src/renderer/src/i18n/en.json'
import fr from '../../src/renderer/src/i18n/fr.json'
import nl from '../../src/renderer/src/i18n/nl.json'

const dictionaries = { EN: en, FR: fr, NL: nl }

describe('i18n resources', () => {
  it('exposes the same keys in every language', () => {
    const reference = Object.keys(dictionaries.EN).sort()
    expect(reference.length).toBeGreaterThan(50)

    for (const [code, dictionary] of Object.entries(dictionaries)) {
      expect(Object.keys(dictionary).sort(), `missing keys in ${code}`).toEqual(reference)
    }
  })

  it('keeps every translation non empty', () => {
    for (const [code, dictionary] of Object.entries(dictionaries)) {
      for (const [key, value] of Object.entries(dictionary)) {
        expect(value, `empty translation for ${code}:${key}`).not.toBe('')
      }
    }
  })

  it('keeps the original key set of the PySide6 GUI', () => {
    const legacyKeys = [
      'credits.text',
      'page_setup_start.text',
      'page_setup_complete.text',
      'page_setup_welcome.text',
      'page_setup_welcome_user.text',
      'page_profile_informations.title',
      'page_profile_firstname.subtitle',
      'page_profile_lastname.subtitle',
      'page_profile_mail.subtitle',
      'page_menu_search.bar',
      'page_menu_tax_toggle_off.label',
      'page_menu_tax_toggle_on.label',
      'page_search_input.placeholder',
      'page_search_add.button',
      'page_search_remove.button',
      'page_search_remove_all.button',
      'page_search_remove_all.title',
      'page_search_remove_all.subtitle',
      'page_search_rapid_access.label',
      'page_settings_save.button',
      'page_settings_general.category',
      'page_settings_websites.category',
      'page_settings_profile.category',
      'page_settings_system.category',
      'page_settings_AI.category',
      'subpage_settings_general_startup.title',
      'subpage_settings_general_startup.subtitle',
      'subpage_settings_general_notification.title',
      'subpage_settings_general_notification.subtitle',
      'subpage_settings_general_open.title',
      'subpage_settings_general_open.subtitle',
      'subpage_settings_general_send_email.title',
      'subpage_settings_general_send_email.subtitle',
      'subpage_settings_websites_cache.title',
      'subpage_settings_websites_0day.label',
      'subpage_settings_websites_1day.label',
      'subpage_settings_websites_3day.label',
      'subpage_settings_websites_7day.label',
      'subpage_settings_websites_14day.label',
      'subpage_settings_profile_firstname.title',
      'subpage_settings_profile_lastname.title',
      'subpage_settings_profile_email.title',
      'subpage_settings_system_update.button',
      'subpage_settings_system_restart.button',
      'subpage_settings_system_reset.button',
    ]

    for (const key of legacyKeys) {
      expect(Object.keys(en)).toContain(key)
    }
  })
})
