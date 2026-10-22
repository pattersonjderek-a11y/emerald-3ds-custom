static const struct LevelUpMove learnset[]={{MOVE_STATUS,1},{MOVE_TACKLE,1},{MOVE_EMBER,7},{LEVEL_UP_MOVE_END,0}};
static const struct LevelUpMove noDamage[]={{MOVE_STATUS,1},{MOVE_EXPLOSION,5},{LEVEL_UP_MOVE_END,0}};
static const struct Evolution treeEvos[]={{EVO_LEVEL,16,SPECIES_GROVYLE},{EVOLUTIONS_END,0,0}};
static const struct Evolution groveEvos[]={{EVO_LEVEL,36,SPECIES_SCEPTILE},{EVOLUTIONS_END,0,0}};
static void InitData(void)
{
    static const unsigned starts[]={1,152,252,387,495,650,722,810,906};
    for(unsigned i=1;i<NUM_SPECIES;++i) bases[i]=i;
    for(unsigned i=1;i<=27;++i) {
        struct SpeciesInfo *p=&gSpeciesInfo[i];
        p->natDexNum=starts[(i-1)/3]+(i-1)%3;
        p->baseHP=p->baseAttack=p->baseDefense=p->baseSpeed=p->baseSpAttack=p->baseSpDefense=50;
        p->frontPic=p->backPic=p->iconSprite=p->palette=p->shinyPalette=learnset;
        p->abilities[0]=1; p->levelUpLearnset=learnset;
    }
    for(unsigned i=28;i<=39;++i) gSpeciesInfo[i]=gSpeciesInfo[7];
    gSpeciesInfo[35].natDexNum=1025; gSpeciesInfo[35].isMythical=true;
    gSpeciesInfo[34].isGalarianForm=true;
    gSpeciesInfo[36].frontPic=NULL;
    gSpeciesInfo[37].isMegaEvolution=true;
    gSpeciesInfo[38].levelUpLearnset=noDamage;
    gSpeciesInfo[39].iconSprite=(void *)1;
    gSpeciesInfo[7].evolutions=treeEvos; gSpeciesInfo[28].evolutions=groveEvos;
    gWildMonHeaders[0].mapGroup=1; gWildMonHeaders[0].mapNum=2;
    gWildMonHeaders[1].mapGroup=1; gWildMonHeaders[1].mapNum=3;
    gWildMonHeaders[2].mapGroup=255;
    static struct WildPokemon mons[12];
    static struct WildPokemonInfo info={20,mons};
    for(unsigned i=0;i<12;++i) mons[i]=(struct WildPokemon){5,8,SPECIES_POOCHYENA};
    for(unsigned map=0;map<2;++map) for(unsigned time=0;time<TIMES_OF_DAY_COUNT;++time)
        gWildMonHeaders[map].encounterTypes[time]=(struct WildEncounterTypes){&info,&info,&info,&info,&info};
    save2.playerTrainerId[0]=123;
}
static struct CRConfig WriteConfig(unsigned options,unsigned generations,unsigned balance,unsigned seed)
{
    struct CRDraft d; CR_Begin(&d,seed,11);
    if(options) { d.config.mode=CR_RANDOMIZED; d.config.algorithm=1; d.config.randomOptions=options; }
    d.config.generations=generations; d.config.balanceFlags=balance;
    assert(CR_Validate(&d.config)==CR_OK && CR_Encode(save1.customRunConfig,123,&d.config));
    return d.config;
}
static void StartersAndPools(void)
{
    struct CRConfig c=WriteConfig(CR_CORE_OPTIONS,256,CR_BALANCE_NO_LEGENDS,42);
    assert(CustomRandom_Validate(&c));
    struct CRConfig evolved=c; evolved.generations=4;
    assert(RivalEvolution(&evolved,7,2,15)==7);
    assert(RivalEvolution(&evolved,7,2,20)==28);
    assert(RivalEvolution(&evolved,7,2,40)==29);
    assert(RivalEvolution(&c,7,2,40)==7); /* generation filter still enforced */
    unsigned evolvedCount=sPoolCount;
    for(unsigned i=0;i<sPoolCount;++i) if(sPool[i].species==28) {
        sPool[i].species=36; /* absent indexed graphics: cannot evolve into it */
        assert(RivalEvolution(&evolved,7,2,40)==7);
        sPool[i].species=28; break;
    }
    assert(sPoolCount==evolvedCount);
    unsigned starters[3];
    for(unsigned i=0;i<3;++i) {
        starters[i]=CustomRandom_Starter(i,7+i);
        assert(starters[i]>=25 && starters[i]<=27);
        for(unsigned j=0;j<i;++j) assert(starters[i]!=starters[j]);
    }
    for(unsigned i=0;i<3;++i) {
        gSpecialVar_Result=i; CB2_GiveStarter();
        assert(selectedStarter==i && gParties[0][0].species==GetStarterPokemon(i));
        assert(gParties[0][0].species==starters[i] && gParties[0][0].moves[0]==MOVE_TACKLE);
    }
    assert(starterCallbacks==12 && GetStarterPokemon(3)==GetStarterPokemon(0));
    unsigned n=sPoolCount;
    assert(n>27);
    for(unsigned i=0;i<n;++i) assert(sPool[i].species!=34 && sPool[i].species!=36 && sPool[i].species!=37 && sPool[i].species!=38 && sPool[i].species!=39);
    struct CRConfig rejected=c; rejected.seed=123456;
    sPoolCount=0;
    assert(!CustomRandom_Validate(&c) && CustomRun_Read(&rejected)==CR_POOL && !CustomRun_CanPlay());
    assert(rejected.seed==123456); /* no output mutation or silent Standard downgrade */
    sPoolCount=n; assert(CustomRun_Read(&rejected)==CR_OK && rejected.seed==42);
    for(unsigned i=0;i<100;++i) { globalRng=i*91; assert(CustomRandom_Starter(0,7)==starters[0]); }
    c=WriteConfig(0,511,0,42); assert(CustomRandom_Validate(&c));
    for(unsigned i=0;i<3;++i) assert(CustomRandom_Starter(i,7+i)==7+i);
    assert(CustomRandom_Starter(99,7)==7);
    puts("native pool/starters: Gen 9-only, distinct/usable, missing art and battle forms excluded, empty-pool rejection, fixed identity PASS");
}
static void WildTables(void)
{
    WriteConfig(CR_RANDOM_WILD,256,CR_BALANCE_NO_LEGENDS,42);
    save1.location.mapGroup=1; save1.location.mapNum=3;
    unsigned cacheBefore=sHeaderNext;
    assert(GetCurrentMapWildMonHeaderId()==1 && sHeaderNext==cacheBefore);
    save1.location.mapGroup=10;
    assert(GetCurrentMapWildMonHeaderId()==HEADER_NONE && sHeaderNext==cacheBefore);
    const struct WildPokemonHeader *p=CustomRandom_Header(0);
    unsigned old[12];
    for(unsigned i=0;i<12;++i) {
        old[i]=p->encounterTypes[0].landMonsInfo->wildPokemon[i].species;
        assert(old[i]>=25 && old[i]<=27);
        assert(p->encounterTypes[0].landMonsInfo->wildPokemon[i].minLevel==5);
        assert(p->encounterTypes[0].landMonsInfo->wildPokemon[i].maxLevel==8);
    }
    assert(p->encounterTypes[0].landMonsInfo->encounterRate==20);
    assert(p->encounterTypes[0].waterMonsInfo->wildPokemon[4].species>=25);
    assert(p->encounterTypes[1].fishingMonsInfo->wildPokemon[9].species>=25);
    for(unsigned i=0;i<50;++i) { globalRng=i; CustomRandom_Header(1); assert(CustomRandom_Header(0)->encounterTypes[0].landMonsInfo->wildPokemon[3].species==old[3]); }
    memset(sHeaders,0,sizeof(sHeaders)); sHeaderNext=0;
    p=CustomRandom_Header(0);
    for(unsigned i=0;i<12;++i) assert(p->encounterTypes[0].landMonsInfo->wildPokemon[i].species==old[i]);
    WriteConfig(CR_RANDOM_WILD,256,CR_BALANCE_NO_LEGENDS,777);
    p=CustomRandom_Header(0); unsigned changes=0;
    for(unsigned i=0;i<12;++i) changes+=p->encounterTypes[0].landMonsInfo->wildPokemon[i].species!=old[i];
    assert(changes);
    WriteConfig(0,511,0,42); assert(CustomRandom_Header(0)==&gWildMonHeaders[0]);
    assert(CustomRandom_Header(2)==&gWildMonHeaders[2]);
    puts("native encounter header: shared land/water/rocks/rod/hidden/TOD mappings, stable reload/cache eviction, levels/rates retained, Standard identity PASS");
}
static void Trainers(void)
{
    static struct TrainerMon mons[6];
    for(unsigned i=0;i<6;++i) {
        mons[i]=(struct TrainerMon){.species=7,.lvl=20+i,.moves={MOVE_ILLEGAL,0,0,0},.heldItem=HOLD_EFFECT_MEGA_STONE,.ability=99,.gender=2,.iv=0x12345678};
    }
    trainers[16]=(struct Trainer){.party=mons,.partySize=4};
    trainers[20]=trainers[16]; trainers[13]=trainers[16]; trainers[13].trainerClass=TRAINER_CLASS_RIVAL;
    struct Pokemon party[6],repeat[6];
    WriteConfig(CR_CORE_OPTIONS,256,CR_BALANCE_NO_LEGENDS,42);
    CustomRandom_BeginTrainer(16);
    unsigned stableSeed=GetPoolSeed(&trainers[16]);
    assert(stableSeed==CustomRandom_TrainerSeed() && GetPoolSeed(&trainers[20])==stableSeed);
    CustomRandom_EndTrainer();
    globalRng=123; CreateNPCTrainerParty(party,16);
    for(unsigned i=0;i<4;++i) {
        assert(party[i].species>=25 && party[i].species<=27 && party[i].level==20+i);
        assert(party[i].source.ability==1 && party[i].source.gender==0 && party[i].source.iv==0x12345678);
        assert(party[i].source.heldItem==ITEM_NONE && party[i].moves[0]==MOVE_EMBER);
        assert(!party[i].source.moves[0] && party[i].source.nickname==NULL);
    }
    globalRng=999999; CreateNPCTrainerParty(repeat,16); assert(!memcmp(party,repeat,sizeof(party)));
    static const struct FormChange mega[]={{FORM_CHANGE_BATTLE_MEGA_EVOLUTION_ITEM,37,123},{FORM_CHANGE_TERMINATOR,0,0}};
    gSpeciesInfo[25].formChangeTable=mega;
    CreateNPCTrainerParty(repeat,16);
    assert(repeat[0].species==25 && repeat[0].source.heldItem==123);
    gSpeciesInfo[25].formChangeTable=NULL;
    CreateNPCTrainerParty(repeat,20); unsigned changes=0;
    for(unsigned i=0;i<4;++i) changes+=repeat[i].species!=party[i].species;
    assert(changes);
    gBattleTypeFlags=BATTLE_TYPE_TWO_OPPONENTS; CreateNPCTrainerParty(party,16);
    assert(party[2].species && !party[3].species); gBattleTypeFlags=0;
    selectedStarter=0; CreateNPCTrainerParty(party,13);
    assert(party[0].species==CustomRandom_Starter(1,SPECIES_TORCHIC));
    mons[0].species=SPECIES_COMBUSKEN; mons[0].lvl=40;
    CreateNPCTrainerParty(repeat,13); assert(repeat[0].species==party[0].species); /* no evolution in Gen 9 fixture */
    WriteConfig(CR_RANDOM_TRAINERS,256,0,42);
    assert(GetStarterPokemon(0)==SPECIES_TREECKO);
    CreateNPCTrainerParty(repeat,13);
    assert(repeat[0].species>=25 && repeat[0].species<=27);
    unsigned trainerOnlyRival=repeat[0].species;
    globalRng=12345; CreateNPCTrainerParty(repeat,13);
    assert(repeat[0].species==trainerOnlyRival);
    mons[1].species=SPECIES_POOCHYENA;
    WriteConfig(CR_RANDOM_STARTERS,256,0,42); CreateNPCTrainerParty(party,13);
    assert(party[0].species==CustomRandom_Starter(1,SPECIES_TORCHIC));
    assert(party[1].species==SPECIES_POOCHYENA && party[1].moves[0]==MOVE_ILLEGAL);
    for(unsigned flag=1;flag<=16;flag<<=1) {
        gBattleTypeFlags=flag; CreateNPCTrainerParty(party,16); assert(party[0].species==mons[0].species);
    }
    gBattleTypeFlags=0;
    WriteConfig(0,511,0,42); CreateNPCTrainerParty(party,16);
    assert(party[0].species==mons[0].species && party[0].moves[0]==MOVE_ILLEGAL);
    puts("production trainer party factory/adapters: deterministic teams, legal replacement moves/abilities/gender/items, levels/IVs/party size, doubles, rival continuity, protected contexts and Standard identity PASS");
}
int main(void) { InitData(); StartersAndPools(); WildTables(); Trainers(); return 0; }
