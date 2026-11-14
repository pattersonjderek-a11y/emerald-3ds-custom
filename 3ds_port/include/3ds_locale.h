#ifndef CTR_LOCALE_H
#define CTR_LOCALE_H

/* The platform sources (3ds_data.c) build without the game's include
 * directories: there, by path. */
#if !defined(PORT_EXPANSION)
#if defined(__has_include) && !__has_include("constants/global.h")
#include "../../include/constants/global.h"
#else
#include "constants/global.h"
#endif

 #endif

/* Native UI literals are converted from UTF-8 into the game font encoding.
 * The port's own interface follows the game's language, or Brazilian
 * Portuguese over the English game when built with PORT_LANG=pt_br
 * (CTR_LANG_PT_BR); the game's own texts stay those of its ROM. */
#if defined(PORT_EXPANSION)
#define CTR_TEXT7(english, spanish, french, italian, portuguese, german, japanese) (english)
#elif CTR_LANG_PT_BR
#define CTR_TEXT7(english, spanish, french, italian, portuguese, german, japanese) (portuguese)
#elif GAME_LANGUAGE == LANGUAGE_SPANISH
#define CTR_TEXT7(english, spanish, french, italian, portuguese, german, japanese) (spanish)
#elif GAME_LANGUAGE == LANGUAGE_FRENCH
#define CTR_TEXT7(english, spanish, french, italian, portuguese, german, japanese) (french)
#elif GAME_LANGUAGE == LANGUAGE_ITALIAN
#define CTR_TEXT7(english, spanish, french, italian, portuguese, german, japanese) (italian)
#elif GAME_LANGUAGE == LANGUAGE_GERMAN
#define CTR_TEXT7(english, spanish, french, italian, portuguese, german, japanese) (german)
#elif GAME_LANGUAGE == LANGUAGE_JAPANESE
#define CTR_TEXT7(english, spanish, french, italian, portuguese, german, japanese) (japanese)
#else
#define CTR_TEXT7(english, spanish, french, italian, portuguese, german, japanese) (english)
#endif

#define CTR_TEXT4(e,s,f,i) CTR_TEXT7(e,s,f,i,e,e,e)
#define CTR_TEXT_PICK(_1,_2,_3,_4,_5,_6,_7,NAME,...) NAME
#define CTR_TEXT(...) CTR_TEXT_PICK(__VA_ARGS__,CTR_TEXT7,CTR_TEXT_BAD6,CTR_TEXT_BAD5,CTR_TEXT4)(__VA_ARGS__)

/* A text only English and Portuguese have. */
#define CTR_TEXT_PT(english, portuguese) CTR_TEXT(english, english, english, english, portuguese, english, english)
/* The same with a German text. */
#define CTR_TEXT_PT_DE(english, portuguese, german) CTR_TEXT(english, english, english, english, portuguese, german, english)

#endif
