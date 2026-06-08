-- Sample seed: thedent.co.th (first design partner) + a small Thai prompt set.
-- Apply with: npm run db:seed:local

INSERT INTO clients (id, name, logo_url, created_at)
VALUES ('client_thedent', 'The Dent', NULL, datetime('now'));

INSERT INTO brands (id, client_id, name, domain, aliases_json, competitors_json, created_at)
VALUES (
  'brand_thedent',
  'client_thedent',
  'The Dent',
  'thedent.co.th',
  '["the dent","เดอะ เดนท์","เดอะเดนท์"]',
  '[{"name":"BIDC","domain":"bangkokdental.com","aliases":["บางกอก อินเตอร์เนชั่นแนล เดนทัล"]},{"name":"Thantakit","domain":"thantakit.com","aliases":["ทันตกิจ"]}]',
  datetime('now')
);

INSERT INTO prompts (id, brand_id, text_th, intent, active, created_at) VALUES
  ('prompt_implant_bkk', 'brand_thedent', 'ทำรากฟันเทียมที่ไหนดี กรุงเทพ', 'commercial', 1, datetime('now')),
  ('prompt_invisalign',  'brand_thedent', 'จัดฟันใสคลินิกไหนดี กรุงเทพ',   'commercial', 1, datetime('now')),
  ('prompt_implant_cost','brand_thedent', 'รากฟันเทียมราคาเท่าไหร่ 2026',  'informational', 1, datetime('now')),
  ('prompt_veneer',      'brand_thedent', 'ทำวีเนียร์ที่ไหนดี รีวิว',       'local', 1, datetime('now'));
