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

/*
 * EXPERIMENT (temporary): raise the renderer's SDR white reference.
 *
 * Under X11 SDL leaves SDL.window.SDR_white_level at its default (1.0 = 80 nits), so the stream is
 * rendered darker than the host sends it. If the file ~/.local/share/decky-stream-hdr/sdr_white
 * exists and holds a number, that number is written to the window property just before the
 * renderer is created. The same file enables a small log (shim.log) of the SDL calls involved.
 * Without the file nothing changes.
 */
typedef struct SDL_Window SDL_Window;
typedef struct SDL_Renderer SDL_Renderer;
typedef bool (*SetFloatPropertyFunction)(SDL_PropertiesID, const char *, float);
typedef float (*GetFloatPropertyFunction)(SDL_PropertiesID, const char *, float);
typedef SDL_PropertiesID (*GetWindowPropertiesFunction)(SDL_Window *);
typedef void *(*GetPointerPropertyFunction)(SDL_PropertiesID, const char *, void *);
typedef SDL_Renderer *(*CreateRendererFunction)(SDL_Window *, const char *);
typedef SDL_Renderer *(*CreateRendererWithPropertiesFunction)(SDL_PropertiesID);

static float experiment_white(void) {
    const char *home = getenv("HOME");
    char path[512];
    if (!home) return 0.0f;
    snprintf(path, sizeof path, "%s/.local/share/decky-stream-hdr/sdr_white", home);
    FILE *file = fopen(path, "r");
    if (!file) return 0.0f;
    float value = 0.0f;
    if (fscanf(file, "%f", &value) != 1) value = 0.0f;
    fclose(file);
    return value;
}

static void experiment_log(const char *format, const char *text, double number) {
    const char *home = getenv("HOME");
    char path[512];
    if (!home) return;
    snprintf(path, sizeof path, "%s/.local/share/decky-stream-hdr/shim.log", home);
    FILE *file = fopen(path, "a");
    if (!file) return;
    fprintf(file, format, text, number);
    fputc('\n', file);
    fclose(file);
}

static void experiment_apply(SDL_Window *window, const char *origin) {
    float white = experiment_white();
    if (white <= 0.0f || !window) return;
    GetWindowPropertiesFunction get_window_properties = (GetWindowPropertiesFunction)dlsym(RTLD_NEXT, "SDL_GetWindowProperties");
    SetFloatPropertyFunction set_float = (SetFloatPropertyFunction)dlsym(RTLD_NEXT, "SDL_SetFloatProperty");
    if (!get_window_properties || !set_float) return;
    set_float(get_window_properties(window), "SDL.window.SDR_white_level", white);
    experiment_log("%s: window SDR_white_level set to %f", origin, white);
}

SDL_Renderer *SDL_CreateRenderer(SDL_Window *window, const char *name) {
    experiment_apply(window, "SDL_CreateRenderer");
    CreateRendererFunction real = (CreateRendererFunction)dlsym(RTLD_NEXT, "SDL_CreateRenderer");
    return real ? real(window, name) : NULL;
}

SDL_Renderer *SDL_CreateRendererWithProperties(SDL_PropertiesID props) {
    GetPointerPropertyFunction get_pointer = (GetPointerPropertyFunction)dlsym(RTLD_NEXT, "SDL_GetPointerProperty");
    if (get_pointer) experiment_apply((SDL_Window *)get_pointer(props, "SDL.renderer.create.window", NULL), "SDL_CreateRendererWithProperties");
    CreateRendererWithPropertiesFunction real = (CreateRendererWithPropertiesFunction)dlsym(RTLD_NEXT, "SDL_CreateRendererWithProperties");
    return real ? real(props) : NULL;
}

bool SDL_SetFloatProperty(SDL_PropertiesID properties, const char *name, float value) {
    if (name && experiment_white() > 0.0f && (strstr(name, "white") || strstr(name, "headroom") || strstr(name, "SDR")))
        experiment_log("SDL_SetFloatProperty %s = %f", name, value);
    SetFloatPropertyFunction real = (SetFloatPropertyFunction)dlsym(RTLD_NEXT, "SDL_SetFloatProperty");
    return real ? real(properties, name, value) : false;
}
