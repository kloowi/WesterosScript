#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')

from ui.desktop_app.bridge import WesterosApi

api = WesterosApi()
result = api.analyze('coin gold claims 100!\nscroll name claims "Arya"!\nraven gold!')
print('=== SEMANTIC OUTPUT ===')
print(result['semantic'])
