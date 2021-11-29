COURSE = cse107
GROUP_NAME = donovan_griego
ASSIGNMENT = contacts
TARGETS = final_contacts.py contacts.json cmds.txt README.md design
zip: $(TARGETS)
	zip $(COURSE)_$(GROUP_NAME)_$(ASSIGNMENT).zip $(TARGETS)
	@echo "\n--- zip archive created ---\n"
	zipinfo $(COURSE)_$(GROUP_NAME)_$(ASSIGNMENT).zip