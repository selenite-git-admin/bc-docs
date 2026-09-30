-- two post-cutover draft members for the race vectors (clone only)
CREATE SCHEMA race;
CREATE FUNCTION race.new_member(tag text) RETURNS uuid LANGUAGE plpgsql AS $f$
DECLARE t mcf.metric_contract_version; u uuid := gen_random_uuid();
BEGIN
  SELECT * INTO t FROM mcf.metric_contract_version WHERE governance_state_code = 'draft' ORDER BY metric_contract_version_uid LIMIT 1;
  t.metric_contract_version_uid := u; t.version_code := 'race-' || tag; t.is_current := false;
  t.governance_state_code := 'draft'; t.aggregation_currency_code := 'not_applicable'; t.created_at := now(); t.supersedes_version_uid := NULL;
  INSERT INTO mcf.metric_contract_version SELECT t.*;
  RETURN u;
END $f$;
CREATE TABLE race.ids (tag text PRIMARY KEY, uid uuid);
INSERT INTO race.ids VALUES ('X', race.new_member('X')), ('Y', race.new_member('Y'));
