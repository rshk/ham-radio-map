TARGETS := data/ei-repeaters.json

all: $(TARGETS)

data/ei-repeaters.json:
	python ./bin/scrape-irts-repeaters.py > $@

clean:
	rm -f $(TARGETS)
