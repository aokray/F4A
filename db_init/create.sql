CREATE TABLE datasets (
    dataset_name TEXT NOT NULL PRIMARY KEY,
    dataset_origin TEXT NOT NULL,
    dataset_sensidx INTEGER NOT NULL,
    dataset_preprocessing TEXT NOT NULL,
    dataset_path TEXT NOT NULL,
    dataset_labeldesc TEXT NOT NULL,
    dataset_featnames TEXT NOT NULL,
    dataset_idxspath TEXT,
    dataset_shortname TEXT NOT NULL,
    dataset_sensnames TEXT NOT NULL,
    dataset_resultsstr TEXT NOT NULL,
    dataset_hdist REAL[] NOT NULL
);

CREATE TABLE algv (
    algv_algname TEXT NOT NULL PRIMARY KEY,
    algv_params BOOLEAN
);

CREATE TABLE paramsv (
    paramsv_alg TEXT NOT NULL,
    paramsv_params TEXT NOT NULL, -- Not null, no alg. MUST be loaded in this table but any that is must have a hyperparameter associated
    paramsv_domain TEXT[] NOT NULL
);

CREATE TABLE webtext (
    webtext_key TEXT NOT NULL PRIMARY KEY,
    webtext_value TEXT NOT NULL
);

CREATE TABLE prun (
    prun_alg TEXT NOT NULL,
    prun_dataset TEXT NOT NULL,
    prun_id INTEGER NOT NULL UNIQUE,
    prun_results JSON NOT NULL,
    prun_feats INTEGER[] NOT NULL,
    CONSTRAINT fk_algname
        FOREIGN KEY (prun_alg)
            REFERENCES algv (algv_algname)
);

CREATE INDEX prun_alg_data
ON prun (prun_alg, prun_dataset);

CREATE TABLE prunhv (
    prunhv_id INTEGER NOT NULL UNIQUE,
    prunhv_name TEXT NOT NULL,
    prunhv_value REAL NOT NULL,
    CONSTRAINT fk_id
        FOREIGN KEY (prunhv_id)
            REFERENCES prun (prun_id),
    CONSTRAINT fk_name
        FOREIGN KEY (prunhv_name)
            REFERENCES algv (algv_algname)
);

CREATE OR REPLACE FUNCTION f_hyperp_check() RETURNS trigger AS $$
    DECLARE
        v_hv_exists BOOLEAN;
    BEGIN
        SELECT paramsv_params = NEW.prunhv_name
        INTO v_hv_exists
        FROM paramsv
        WHERE paramsv_params = NEW.prunhv_name;

        IF v_hv_exists THEN
            RETURN NEW;
        ELSE
            RAISE EXCEPTION 'Cannot insert hyperparameter % into prunhv without a matching value in paramsv_params', NEW.prunhv_name;
        END IF;

    END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER f_hyperp_check BEFORE INSERT OR UPDATE ON prunhv
    FOR EACH ROW EXECUTE PROCEDURE f_hyperp_check();