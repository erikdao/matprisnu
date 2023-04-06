DIST_DIR=dist/
SCRAPRER_SRC=src/python/scrappers
SCRAPPER_TARGET=$(SCRAPRER_SRC):scrappers-cli
SCRAPPER_PEX_FILE=scrappers-cli.pex
SCRAPPER_PEX=$(DIST_DIR)$(SCRAPPER_PEX_FILE)

all: clean build

clean:
	rm -rf $(DIST_DIR)

build:
	pants package $(SCRAPPER_TARGET)
