static const struct LevelUpMove moves[]={{MOVE_STATUS,1},{MOVE_TACKLE,1},{MOVE_EMBER,7},{LEVEL_UP_MOVE_END,0}};
static struct CRConfig SaveRules(unsigned preset,bool randomized)
{
    struct CRDraft d;
    CR_Begin(&d,42,77); CR_SetDifficulty(&d.config,preset);
    if(randomized) { d.config.mode=CR_RANDOMIZED; d.config.algorithm=1; d.config.randomOptions=CR_CORE_OPTIONS; }
    assert(CR_Confirm(&d) && CR_Commit(&d,save1.customRunConfig,123));
    struct CRConfig out; assert(CR_Decode(save1.customRunConfig,123,&out)==CR_OK); return out;
}
static void Setup(void)
{
    for(unsigned i=1;i<=27;++i) {
        bases[i]=i;
        gSpeciesInfo[i]=(struct SpeciesInfo){.natDexNum=i<25?i:906+i-25,.baseHP=50,.baseAttack=50,.baseDefense=50,.baseSpAttack=50,.baseSpDefense=50,.baseSpeed=50,
          .types={0,1},.abilities={1,0,0},.levelUpLearnset=moves,
          .frontPic=moves,.backPic=moves,.iconSprite=moves,.palette=moves,.shinyPalette=moves};
    }
    save2.playerTrainerId[0]=123;
    static struct TrainerMon normal[6],hard[6];
    for(unsigned i=0;i<6;++i) {
        normal[i]=(struct TrainerMon){.species=7,.lvl=12+i,.moves={MOVE_TACKLE,0,0,0},.iv=12};
        hard[i]=normal[i];hard[i].iv=31;hard[i].heldItem=1;
    }
    trainers[16]=(struct Trainer){.partySize=4,.party=normal,.aiFlags=AI_FLAG_CHECK_BAD_MOVE};
    gTrainers[DIFFICULTY_HARD][16]=(struct Trainer){.partySize=4,.party=hard,.aiFlags=AI_FLAG_CHECK_BAD_MOVE};
    trainers[17]=trainers[16]; /* Native fallback if no prepared variant. */
}
static void SavedRules(void)
{
    struct CRConfig c,out,before;
    uint8_t saved[52];
    for(unsigned mode=0;mode<2;++mode) for(unsigned preset=0;preset<3;++preset) {
        c=SaveRules(preset,mode);
        assert(CR_Decode(save1.customRunConfig,123,&out)==CR_OK && out.difficulty==preset);
        memcpy(saved,save1.customRunConfig,52);
        for(unsigned i=0;i<100;++i) { assert(CustomRun_Read(&out)==CR_OK); assert(out.seed==42 && out.difficultyOptions==c.difficultyOptions); }
        assert(!memcmp(saved,save1.customRunConfig,52));
    }
    c=SaveRules(CR_CUSTOM,true);
    for(unsigned cap=0;cap<3;++cap) for(unsigned ai=0;ai<2;++ai) for(unsigned bits=0;bits<16;++bits) {
        c.capMode=cap;c.aiPolicy=ai;c.difficultyOptions=bits;
        assert(CR_Encode(saved,123,&c) && CR_Decode(saved,123,&out)==CR_OK);
        assert(out.capMode==cap && out.aiPolicy==ai && out.difficultyOptions==bits);
    }
    c.capMode=3; assert(CR_Validate(&c)==CR_RULES);
    c.capMode=0;c.aiPolicy=2;assert(CR_Validate(&c)==CR_RULES);
    c.aiPolicy=0;c.difficultyOptions=16;assert(CR_Validate(&c)==CR_RULES);
    c.difficultyOptions=0;c.contentRules=CR_RULES_STAGE_C;c.difficulty=CR_HARD;assert(CR_Validate(&c)!=CR_OK);
    c.difficulty=CR_NORMAL;assert(CR_Validate(&c)==CR_OK); /* Historical C seed/key remains supported. */
    SaveRules(CR_HARD,true); before=c;
    save1.customRunConfig[16]^=1; assert(CustomRun_Read(&c)==CR_CORRUPT && !memcmp(&c,&before,sizeof(c)));
    struct CRDraft draft; CR_Begin(&draft,99,9); assert(draft.config.difficulty==CR_NORMAL && !draft.config.difficultyOptions);
    memcpy(saved,save1.customRunConfig,52);CR_SetDifficulty(&draft.config,CR_HARD);CR_Cancel(&draft);
    assert(!CR_Commit(&draft,save1.customRunConfig,123) && !memcmp(saved,save1.customRunConfig,52));
    puts("difficulty save: both modes/presets, 96 Custom combinations, invalid bits, legacy C, corruption, reset, cancellation and immutable Continue PASS");
}
static void Caps(void)
{
    const unsigned caps[]={15,19,24,29,31,33,42,46,58};
    struct Pokemon mon={.species=1,.level=10};
    SaveRules(CR_HARD,false);
    for(unsigned stage=0;stage<9;++stage) {
        memset(flags,0,sizeof(flags)); for(unsigned i=0;i<stage;++i) flags[FLAG_BADGE01_GET+i]=true;
        assert(CustomDifficulty_ProgressCap()==caps[stage] && GetCurrentLevelCap()==caps[stage]);
        mon.level=caps[stage]-1;
        unsigned reward=caps[stage]*caps[stage]*caps[stage]-mon.level*mon.level*mon.level;
        assert(CustomDifficulty_ClampExp(&mon,UINT32_MAX)==reward);
        assert(CustomDifficulty_ClampExp(&mon,1)==1);
        assert(GetSoftLevelCapExpValue(mon.level,400)==400); /* No grind penalty. */
        mon.level=caps[stage];assert(!CustomDifficulty_ClampExp(&mon,400) && !GetSoftLevelCapExpValue(mon.level,400));
        assert(!TryIncrementMonLevel(&mon));
        mon.level=caps[stage]+1; assert(!CustomDifficulty_ClampExp(&mon,UINT32_MAX));
    }
    flags[FLAG_IS_CHAMPION]=true;
    assert(GetCurrentLevelCap()==100); /* League stays 58 through Champion, then all rematches/postgame uncapped. */
    mon.level=99;assert(CustomDifficulty_ClampExp(&mon,UINT32_MAX)==1000000-970299);
    mon.level=100;assert(!CustomDifficulty_ClampExp(&mon,1));
    struct CRConfig c=SaveRules(CR_CUSTOM,false);c.capMode=CR_CAP_SOFT;assert(CR_Encode(save1.customRunConfig,123,&c));
    memset(flags,0,sizeof(flags));assert(CustomDifficulty_ProgressCap()==15 && GetCurrentLevelCap()==100);
    assert(GetSoftLevelCapExpValue(14,640)==640 && GetSoftLevelCapExpValue(15,640)==160);
    assert(GetSoftLevelCapExpValue(16,640)==80 && GetSoftLevelCapExpValue(99,640)==10);
    mon.level=20;assert(CustomDifficulty_ClampExp(&mon,UINT32_MAX)==UINT32_MAX);
    SaveRules(CR_NORMAL,false);assert(GetCurrentLevelCap()==100 && GetSoftLevelCapExpValue(90,640)==640);
    assert(CR_ProgressCap(0xFE,false)==15); /* First missing badge, not badge count. */
    puts("native caps/reward: all 8 gyms, whole League, Champion unlock, postgame/rematches, multi-level overflow, over-cap gifts, soft/hard/off PASS");
}
static void ItemsAndAi(void)
{
    struct CRConfig c=SaveRules(CR_HARD,false);
    gSaveBlock2Ptr->optionsBattleStyle=0;gBattleScripting.windowsType=9;gBattleScripting.specialTrainerBattleType=7;
    ClearSetBScriptingStruct();assert(gBattleScripting.battleStyle==OPTIONS_BATTLE_STYLE_SET && gBattleScripting.windowsType==9 && gBattleScripting.specialTrainerBattleType==7);
    assert(gSaveBlock2Ptr->optionsBattleStyle==0); /* Preserve the player's preference. */
    gBattleTypeFlags=BATTLE_TYPE_TRAINER;
    for(unsigned item=1;item<=EFFECT_ITEM_USE_POKE_FLUTE;++item) {
        bool blocked=item!=EFFECT_ITEM_ESCAPE && item!=EFFECT_ITEM_THROW_BALL && item!=EFFECT_ITEM_USE_POKE_FLUTE;
        assert(CustomDifficulty_ItemBlocked(item)==blocked);
    }
    const unsigned protected[]={0,BATTLE_TYPE_LINK,BATTLE_TYPE_RECORDED,BATTLE_TYPE_FRONTIER,BATTLE_TYPE_TRAINER_HILL,BATTLE_TYPE_SECRET_BASE,BATTLE_TYPE_EREADER_TRAINER,BATTLE_TYPE_FIRST_BATTLE,BATTLE_TYPE_CATCH_TUTORIAL,BATTLE_TYPE_POKEDUDE};
    for(unsigned i=0;i<ARRAY_COUNT(protected);++i) {
        gBattleTypeFlags=i ? BATTLE_TYPE_TRAINER|protected[i] : 0;
        assert(!CustomDifficulty_ItemBlocked(EFFECT_ITEM_RESTORE_HP));
        assert(CustomDifficulty_AiFlags(16,1,AI_FLAG_OMNISCIENT)==AI_FLAG_OMNISCIENT);
    }
    gBattleTypeFlags=BATTLE_TYPE_TRAINER;
    u64 cheats=AI_FLAG_OMNISCIENT|AI_FLAG_MOVE_OMNISCIENCE|AI_FLAG_ABILITY_OMNISCIENCE|AI_FLAG_ITEM_OMNISCIENCE|AI_FLAG_PREDICTION|AI_FLAG_ASSUMPTIONS|AI_FLAG_KNOW_OPPONENT_PARTY;
    u64 ai=CustomDifficulty_AiFlags(16,1,cheats);
    assert(!(ai&cheats) && (ai&AI_FLAG_BASIC_TRAINER)==AI_FLAG_BASIC_TRAINER && (ai&AI_FLAG_SMART_SWITCHING));
    assert(CustomDifficulty_AiFlags(16,0,cheats)==cheats && CustomDifficulty_AiFlags(65535,1,cheats)==cheats);
    ai=GetAiFlags(16,B_BATTLER_1);assert(ai&AI_FLAG_HP_AWARE);assert(!(ai&cheats));
    gBattleTypeFlags|=BATTLE_TYPE_TWO_OPPONENTS;assert(GetAiFlags(16,B_BATTLER_3)&AI_FLAG_DOUBLE_BATTLE);
    gBattleTypeFlags=BATTLE_TYPE_TRAINER;
    c=SaveRules(CR_CUSTOM,false);c.difficultyOptions=CR_NO_HEAL;assert(CR_Encode(save1.customRunConfig,123,&c));
    assert(CustomDifficulty_ItemBlocked(EFFECT_ITEM_REVIVE) && !CustomDifficulty_ItemBlocked(EFFECT_ITEM_INCREASE_STAT));
    c.difficultyOptions=CR_BOSS_PREP;assert(CR_Encode(save1.customRunConfig,123,&c));
    assert(GetAiFlags(16,B_BATTLER_1)==trainers[16].aiFlags); /* Prepared bosses must not force tactical AI. */
    c.difficultyOptions=CR_NO_BOOST;assert(CR_Encode(save1.customRunConfig,123,&c));
    assert(!CustomDifficulty_ItemBlocked(EFFECT_ITEM_REVIVE) && CustomDifficulty_ItemBlocked(EFFECT_ITEM_INCREASE_STAT));
    SaveRules(CR_NORMAL,false);ClearSetBScriptingStruct();assert(gBattleScripting.battleStyle==0);assert(!CustomDifficulty_ForceSet() && !CustomDifficulty_ItemBlocked(EFFECT_ITEM_INCREASE_STAT));
    assert(GetAiFlags(16,B_BATTLER_1)==trainers[16].aiFlags);
    puts("native AI/item rules: tactical flags, hidden-knowledge mask, doubles, allies/facilities/tutorial protections, balls/key items, independent heal/boost options PASS");
}
static void Composition(void)
{
    struct Pokemon fixed[6],random[6],again[6];
    gBattleTypeFlags=BATTLE_TYPE_TRAINER;
    for(unsigned preset=0;preset<3;++preset) {
        struct CRConfig c=SaveRules(preset,false);
        if(preset==CR_CUSTOM) { c.difficultyOptions=CR_BOSS_PREP;assert(CR_Encode(save1.customRunConfig,123,&c)); }
        CreateNPCTrainerParty(fixed,16);
        assert(fixed[0].species==7 && fixed[0].source.iv==(preset==CR_NORMAL ? 12 : 31));
        c.mode=CR_RANDOMIZED;c.algorithm=1;c.randomOptions=CR_CORE_OPTIONS;c.generations=256;
        assert(CR_Encode(save1.customRunConfig,123,&c));
        globalRng=1; CreateNPCTrainerParty(random,16);
        for(unsigned i=0;i<4;++i) {
            assert(random[i].species>=25 && random[i].species<=27 && random[i].species!=fixed[i].species);
            assert(random[i].level==fixed[i].level && random[i].source.iv==fixed[i].source.iv);
            assert(random[i].moves[0] && random[i].moves[0]!=MOVE_ILLEGAL && random[i].source.ability==1);
        }
        for(unsigned i=0;i<4;++i) for(unsigned j=0;j<4;++j)
            assert(!random[i].moves[j] || random[i].moves[j]==MOVE_TACKLE || random[i].moves[j]==MOVE_EMBER || random[i].moves[j]==MOVE_STATUS);
        assert(!sPreparedTrainer && !sTrainerContext);
        globalRng=234567;CreateNPCTrainerParty(again,16);assert(!memcmp(random,again,sizeof(random)));
        gBattleTypeFlags|=BATTLE_TYPE_TWO_OPPONENTS;CreateNPCTrainerParty(again,16);
        assert(again[2].species && !again[3].species);gBattleTypeFlags=BATTLE_TYPE_TRAINER;
        CreateNPCTrainerParty(again,17);assert(again[0].source.iv==12); /* Missing variant falls back safely. */
        CreateNPCTrainerPartyFromTrainer(again,&trainers[16]);assert(again[0].species==7); /* No leaked opponent context into ally/script factory. */
    }
    puts("production party factory: Normal/Hard/Custom templates before seeded species; boss randomization survives, legal moves, retained levels/size, doubles, reset determinism, no context leaks PASS");
}
static void MenuRules(void)
{
    struct CRMenu m; char lines[12][36];
    CR_MenuBegin(&m,42,77);
    CR_MenuInput(&m,CR_A,0); /* Standard is default; difficulty remains independent. */
    m.selected=2;CR_MenuInput(&m,CR_A,0);assert(m.page==CR_PAGE_DIFFICULTY_CUSTOM);
    const unsigned bits[]={CR_FORCE_SET,CR_NO_HEAL,CR_NO_BOOST};
    CR_MenuInput(&m,CR_A,0);assert(m.draft.config.capMode==CR_CAP_HARD);
    CR_MenuInput(&m,CR_A,0);assert(m.draft.config.capMode==CR_CAP_SOFT);
    for(unsigned i=1;i<=3;++i) { m.selected=i;CR_MenuInput(&m,CR_A,0);assert(m.draft.config.difficultyOptions&bits[i-1]); }
    m.selected=4;CR_MenuInput(&m,CR_A,0);assert(m.draft.config.aiPolicy==CR_AI_TACTICAL);
    m.selected=5;CR_MenuInput(&m,CR_A,0);assert(m.draft.config.difficultyOptions&CR_BOSS_PREP);
    m.selected=6;CR_MenuInput(&m,CR_A,0);assert(m.page==CR_PAGE_SEED);
    m.selected=3;CR_MenuInput(&m,CR_A,0);assert(m.page==CR_PAGE_SUMMARY);
    CR_MenuInput(&m,CR_RIGHT,0); CR_MenuLines(&m,lines);
    assert(!strcmp(lines[4],"CAP: SOFT") && !strcmp(lines[5],"STYLE: SET"));
    assert(strstr(lines[6],"BLOCKED") && strstr(lines[8],"TACTICAL"));
    assert(CR_MenuInput(&m,CR_A,0)==CR_ACCEPTED);
    puts("production setup: Standard + independent Custom rules, soft caps, style, separate bag policies, AI, prepared bosses, readable confirmation PASS");
}
int main(void) { Setup();SavedRules();Caps();ItemsAndAi();Composition();MenuRules();ActualItemCallback();CandiesAndDaycare();return 0; }
