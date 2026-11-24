/*
 * StreamHDR injection library.
 *
 * Steam's Linux streaming client asks SDL3 whether the display has HDR enabled
 * (SDL.display.HDR_enabled). Under X11 SDL always answers "no", so the client
 * requests an SDR stream. Preloading this library makes that one query answer
 * "yes"; every other property lookup is forwarded to the real SDL.
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

/* Pin dlsym to an old glibc version so the library also loads inside the Steam
 * runtime container, which ships an older glibc. Required. */
__asm__(".symver dlsym, dlsym@GLIBC_2.2.5");

typedef uint32_t SDL_PropertiesID;
typedef bool (*GetBooleanPropertyFunction)(SDL_PropertiesID, const char *, bool);

bool SDL_GetBooleanProperty(SDL_PropertiesID properties, const char *name, bool default_value) {
    if (name && strcmp(name, "SDL.display.HDR_enabled") == 0) return true;

    static GetBooleanPropertyFunction real_get_boolean_property = NULL;
    if (!real_get_boolean_property)
        real_get_boolean_property = (GetBooleanPropertyFunction)dlsym(RTLD_NEXT, "SDL_GetBooleanProperty");

    return real_get_boolean_property ? real_get_boolean_property(properties, name, default_value) : default_value;
}
