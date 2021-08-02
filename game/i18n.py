import os
import json

open('saves/.lang', 'a').close() # create file empty if not exists

with open('saves/.lang', 'r') as lang:
    LANG = lang.read().strip()

if not LANG: # none set
    # list of supported languages
    langs = [name[:-5] for name in os.listdir('i18n')
             if name.endswith('.json')]
    langcount = len(langs) # precompute
    for i, langcode in enumerate(langs, start=1):
        with open('i18n/%s.json' % langcode, 'r') as lang:
            data = json.load(lang)
        # e.g. "1) English"
        print('%s) %s' % (i, data['lang-name']))
    choice = 0
    while choice - 1 not in range(langcount):
        # e.g. "1-5: "
        choice = input('1-%s: ' % langcount)
        try:
            choice = int(choice)
        except ValueError:
            continue
    LANG = langs[choice - 1]
    with open('saves/.lang', 'w') as lang:
        lang.write(LANG)

with open('i18n/%s.json' % LANG) as lang:
    STRINGS: dict[str, str] = json.load(lang)

def i18n(key: str, *args) -> str:
    return STRINGS[key].format(*args)

def pi18n(key: str, *args, **print_kwargs):
    print(i18n(key, *args), **print_kwargs)