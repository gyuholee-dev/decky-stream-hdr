# Native build entry point used by the Decky store CI and local builds.
# Output must end up in ./out so it is packaged into the plugin's bin/ directory.
CC ?= gcc
CFLAGS ?= -O2

.PHONY: all clean
all: out/sdl_hdr_shim.so

out/sdl_hdr_shim.so: src/sdl_hdr_shim.c
	mkdir -p out
	$(CC) -shared -fPIC $(CFLAGS) -o $@ $< -ldl

clean:
	rm -rf out
