LIBNAME youtube "/home/u64464196/Proiect";

/* CERINTA 1 - Crearea unui set de date SAS din fisiere externe */
PROC IMPORT
    DATAFILE = "/home/u64464196/Proiect/global_youtube_statistics.xlsx"
    OUT      = youtube.yt_raw
    DBMS     = XLSX
    REPLACE;
    SHEET = "global_youtube_statistics";
    GETNAMES = YES;
RUN;

DATA youtube.yt_raw;
    SET youtube.yt_raw;
    RENAME 'video views'N = video_views;
RUN;

/* CERINTA 2: crearea și folosirea de formate definite de utilizator*/
PROC FORMAT LIBRARY = youtube;
    VALUE tier_fmt
        LOW      -< 1000000  = "Micro (sub 1M)"
        1000000  -< 5000000  = "Mid (1M-5M)"
        5000000  -< 20000000 = "Major (5M-20M)"
        20000000 - HIGH      = "Mega (peste 20M)";

    VALUE venit_fmt
        LOW      -< 100000   = "Sub 100K"
        100000   -< 1000000  = "100K - 1M"
        1000000  -< 10000000 = "1M - 10M"
        10000000 - HIGH      = "Peste 10M";

    VALUE $ tara_fmt
        "United States"  = "SUA"
        "India"          = "India"
        "Brazil"         = "Brazilia"
        "United Kingdom" = "Marea Britanie"
        "South Korea"    = "Coreea de Sud"
        "Russia"         = "Rusia"
        "Japan"          = "Japonia"
        "Germany"        = "Germania"
        OTHER            = "Alta tara";

    VALUE $ tip_canal_fmt
        "Music"          = "Muzica"
        "Entertainment"  = "Entertainment"
        "Gaming"         = "Gaming"
        "Education"      = "Educatie"
        "News"           = "Stiri"
        "Sports"         = "Sport"
        OTHER            = "Altele";
RUN;

/* CERINTA 3 - procesarea iterativă și condițională a datelor*/
DATA youtube.yt_procesat;
    SET youtube.yt_raw;

    IF lowest_yearly_earnings  = . THEN lowest_yearly_earnings  = 0;
    IF highest_yearly_earnings = . THEN highest_yearly_earnings = 0;
    IF lowest_monthly_earnings = . THEN lowest_monthly_earnings = 0;
    IF highest_monthly_earnings= . THEN highest_monthly_earnings= 0;
    IF uploads = . THEN uploads = 0;

    yearly_earnings_avg  = (lowest_yearly_earnings  + highest_yearly_earnings)  / 2;
    monthly_earnings_avg = (lowest_monthly_earnings + highest_monthly_earnings) / 2;

    IF subscribers > 0 THEN
        engagement_rate = video_views / subscribers;
    ELSE
        engagement_rate = 0;

    IF subscribers < 1000000 THEN tier = "Micro";
    ELSE IF subscribers < 5000000 THEN tier = "Mid";
    ELSE IF subscribers < 20000000 THEN tier = "Major";
    ELSE tier = "Mega";

    IF yearly_earnings_avg < 100000 THEN segment_venit = "Sub 100K";
    ELSE IF yearly_earnings_avg < 1000000 THEN segment_venit = "100K-1M";
    ELSE IF yearly_earnings_avg < 10000000 THEN segment_venit = "1M-10M";
    ELSE segment_venit = "Peste 10M";

/* CERINTA 5- utilizarea de functii sas */

    scor_subscribers = MIN(subscribers / 50000000 * 25, 25);
    scor_views       = MIN(video_views / 10000000000 * 25, 25);
    scor_earnings    = MIN(yearly_earnings_avg / 20000000 * 25, 25);
    scor_engagement  = MIN(engagement_rate / 300 * 25, 25);
    scor_total       = SUM(scor_subscribers, scor_views, scor_earnings, scor_engagement);

    IF scor_total >= 75 THEN performanta = "Excelent";
    ELSE IF scor_total >= 50 THEN performanta = "Bun";
    ELSE IF scor_total >= 25 THEN performanta = "Mediu";
    ELSE performanta = "In crestere";

    log_subscribers = LOG(subscribers + 1);
    log_views       = LOG(video_views + 1);
    log_earnings    = LOG(yearly_earnings_avg + 1);

    IF NOT MISSING(created_year) THEN vechime_ani = 2024 - created_year;
    ELSE vechime_ani = .;

    FORMAT subscribers            tier_fmt.
           yearly_earnings_avg    venit_fmt.
           Country                $tara_fmt.
           category               $tip_canal_fmt.;
RUN;
/*CERINTA 4 - Crearea de subseturi de date*/
DATA youtube.yt_mega;
    SET youtube.yt_procesat;
    WHERE tier = "Mega";
RUN;

DATA youtube.yt_usa_india;
    SET youtube.yt_procesat;
    WHERE Country IN ("United States", "India");
RUN;

%LET dsid = %SYSFUNC(OPEN(youtube.yt_usa_india));
%LET nobs = %SYSFUNC(ATTRN(&dsid, NOBS));
%LET rc = %SYSFUNC(CLOSE(&dsid));
%PUT NOTE: Canale SUA+India = &nobs;


PROC MEANS DATA = youtube.yt_procesat NOPRINT;
    VAR yearly_earnings_avg;
    OUTPUT OUT = _medii MEAN = medie_earn;
RUN;

DATA _null_;
    SET _medii;
    CALL SYMPUTX("medie_earn", medie_earn);
RUN;

DATA youtube.yt_top_earners;
    SET youtube.yt_procesat;
    WHERE yearly_earnings_avg > &medie_earn;
RUN;

/*cerinta 6 - combinarea seturilor de date prin proceduri specifice SAS și SQL*/
PROC MEANS DATA = youtube.yt_procesat NOPRINT;
    CLASS category;
    VAR subscribers yearly_earnings_avg engagement_rate;
    OUTPUT OUT = youtube.agg_categorie (DROP=_TYPE_ _FREQ_)
           MEAN = sub_mediu_cat earn_mediu_cat eng_mediu_cat;
RUN;

PROC SORT DATA = youtube.yt_procesat; BY category; RUN;
PROC SORT DATA = youtube.agg_categorie; BY category; RUN;

DATA youtube.yt_cu_agg_cat;
    MERGE youtube.yt_procesat(IN=a)
          youtube.agg_categorie(IN=b);
    BY category;
    IF a;
RUN;

PROC SQL;
    CREATE TABLE youtube.yt_sql_join AS
    SELECT t1.*, t2.sub_mediu_cat
    FROM youtube.yt_procesat t1
    LEFT JOIN youtube.agg_categorie t2
    ON t1.category = t2.category;
QUIT;

/*cerinta 7 - utilizarea de proceduri pentru raportare*/
PROC REPORT DATA = youtube.yt_procesat NOWD;
    COLUMN category subscribers yearly_earnings_avg engagement_rate scor_total;

    DEFINE category / GROUP;
    DEFINE subscribers / MEAN;
    DEFINE yearly_earnings_avg / MEAN;
    DEFINE engagement_rate / MEAN;
    DEFINE scor_total / MEAN;
RUN;

/*cerinta 8 - folosirea de proceduri statistice*/
PROC CORR DATA = youtube.yt_procesat;
    VAR log_subscribers log_views log_earnings engagement_rate uploads;
RUN;

PROC REG DATA = youtube.yt_procesat;
    MODEL log_earnings = log_subscribers log_views engagement_rate uploads;
RUN;
QUIT;

PROC ANOVA DATA = youtube.yt_procesat;
    CLASS tier;
    MODEL yearly_earnings_avg = tier;
RUN;
QUIT;

/*cerinta 9 - Generarea de grafice*/
PROC SGPLOT DATA = youtube.yt_procesat;
    SCATTER X=log_subscribers Y=log_earnings;
RUN;

/* CERINTA 10 - Utilizarea de masive */

DATA youtube.yt_procesat_array;
    SET youtube.yt_procesat;

    ARRAY indicatori[4] subscribers video_views yearly_earnings_avg engagement_rate;
    ARRAY indicatori_norm[4] norm_subscribers norm_views norm_earnings norm_engagement;

    DO i = 1 TO DIM(indicatori);
        IF indicatori[i] > 0 THEN indicatori_norm[i] = indicatori[i] / (indicatori[i] + 1);
        ELSE indicatori_norm[i] = 0;
    END;

    DROP i;
RUN;

PROC EXPORT
    DATA    = youtube.yt_procesat
    OUTFILE = "/home/u64464196/Proiect/yt_final_procesat.csv"
    DBMS    = CSV
    REPLACE;
RUN;
