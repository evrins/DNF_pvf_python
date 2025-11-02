uic:
	pyside6-uic ui/components/inventory/empty.ui -o ui/components/inventory/empty_ui.py
	pyside6-uic ui/components/inventory/inventory_equipment_form.ui -o ui/components/inventory/inventory_equipment_form_ui.py
	pyside6-uic ui/components/inventory/inventory_stackable_form.ui -o ui/components/inventory/inventory_stackable_form_ui.py
	pyside6-uic ui/components/inventory/inventory.ui -o ui/components/inventory/inventory_ui.py
	pyside6-uic ui/components/settings/settings.ui -o ui/components/settings/settings_ui.py
	pyside6-uic ui/components/equipment_search/equipment_search.ui -o ui/components/equipment_search/equipment_search_ui.py
	pyside6-uic ui/components/stackable_search/stackable_search.ui -o ui/components/stackable_search/stackable_search_ui.py
