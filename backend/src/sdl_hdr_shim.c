/*
 * StreamHDR injection library.
 *
 * Steam's Linux streaming client asks SDL3 whether the display has HDR enabled
 * (SDL.display.HDR_enabled). Under X11 SDL always answers "no", so the client
 * requests an SDR stream. Preloading this library makes that one query answer
 * "yes"; every other property lookup is forwarded to the real SDL.
 *
 * It also sets the paper white of the renderer. Under X11 SDL leaves the window property
 * SDL.window.SDR_white_level at 1.0 (80 nits), which draws the whole stream about three times
 * darker than the host sends it. The wanted paper white, in nits, is read from the file
 * paper_white in the plugin data folder just before the renderer is created.
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
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


#define SDL_REFERENCE_WHITE_NITS 80.0f /* SDL counts white levels in units of 80 nits */
#define PAPER_WHITE_DEFAULT_NITS 200.0f
#define PAPER_WHITE_MIN_NITS 80.0f
#define PAPER_WHITE_MAX_NITS 480.0f

typedef struct SDL_Window SDL_Window;
typedef struct SDL_Renderer SDL_Renderer;
typedef bool (*SetFloatPropertyFunction)(SDL_PropertiesID, const char *, float);
typedef SDL_PropertiesID (*GetWindowPropertiesFunction)(SDL_Window *);
typedef void *(*GetPointerPropertyFunction)(SDL_PropertiesID, const char *, void *);
typedef SDL_Renderer *(*CreateRendererFunction)(SDL_Window *, const char *);
typedef SDL_Renderer *(*CreateRendererWithPropertiesFunction)(SDL_PropertiesID);

/* Paper white in nits: the value saved by the plugin, or the default when the file is missing or invalid. */
static float paper_white_nits(void) {
    const char *home = getenv("HOME");
    if (!home) return PAPER_WHITE_DEFAULT_NITS;
    char path[512];
    snprintf(path, sizeof path, "%s/.local/share/decky-stream-hdr/paper_white", home);
    FILE *file = fopen(path, "r");
    if (!file) return PAPER_WHITE_DEFAULT_NITS;
    float nits = 0.0f;
    int read = fscanf(file, "%f", &nits);
    fclose(file);
    if (read != 1 || nits < PAPER_WHITE_MIN_NITS || nits > PAPER_WHITE_MAX_NITS) return PAPER_WHITE_DEFAULT_NITS;
    return nits;
}

static void apply_paper_white(SDL_Window *window) {
    if (!window) return;
    GetWindowPropertiesFunction get_window_properties = (GetWindowPropertiesFunction)dlsym(RTLD_NEXT, "SDL_GetWindowProperties");
    SetFloatPropertyFunction set_float_property = (SetFloatPropertyFunction)dlsym(RTLD_NEXT, "SDL_SetFloatProperty");
    if (!get_window_properties || !set_float_property) return;
    set_float_property(get_window_properties(window), "SDL.window.SDR_white_level", paper_white_nits() / SDL_REFERENCE_WHITE_NITS);
}

SDL_Renderer *SDL_CreateRenderer(SDL_Window *window, const char *name) {
    apply_paper_white(window);
    CreateRendererFunction real = (CreateRendererFunction)dlsym(RTLD_NEXT, "SDL_CreateRenderer");
    return real ? real(window, name) : NULL;
}

SDL_Renderer *SDL_CreateRendererWithProperties(SDL_PropertiesID props) {
    GetPointerPropertyFunction get_pointer_property = (GetPointerPropertyFunction)dlsym(RTLD_NEXT, "SDL_GetPointerProperty");
    if (get_pointer_property) apply_paper_white((SDL_Window *)get_pointer_property(props, "SDL.renderer.create.window", NULL));
    CreateRendererWithPropertiesFunction real = (CreateRendererWithPropertiesFunction)dlsym(RTLD_NEXT, "SDL_CreateRendererWithProperties");
    return real ? real(props) : NULL;
}
