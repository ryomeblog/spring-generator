/* テーブルが存在する場合は削除 */
DROP TABLE IF EXISTS todo_tbl;

DROP TABLE IF EXISTS user_tbl;

DROP TABLE IF EXISTS group_tbl;

/* ユーザテーブル作成 */
CREATE TABLE user_tbl(
	user_id VARCHAR(15) NOT NULL,
	password VARCHAR NOT NULL,
	user_name VARCHAR(100) NOT NULL,
	error_password SMALLINT,
	lock BOOLEAN,
	authority SMALLINT NOT NULL DEFAULT 0,
	version SMALLINT NOT NULL DEFAULT 0,
	PRIMARY KEY(user_id)
);

/* グループテーブル作成 */
CREATE TABLE group_tbl(
	group_id VARCHAR(11) NOT NULL,
	group_name VARCHAR(200) NOT NULL,
	user_id VARCHAR(15),
	version SMALLINT NOT NULL DEFAULT 0,
	PRIMARY KEY(group_id),
	FOREIGN KEY(user_id) REFERENCES user_tbl(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

/* TODOリストテーブル作成 */
CREATE TABLE todo_tbl(
	todo_id VARCHAR(11) NOT NULL,
	group_id VARCHAR(11) NOT NULL,
	todo_name VARCHAR(200) NOT NULL,
	todo_status BOOLEAN NOT NULL,
	todo_memo VARCHAR(1000),
	user_id VARCHAR(15),
	version SMALLINT NOT NULL DEFAULT 0,
	PRIMARY KEY(todo_id, group_id),
	FOREIGN KEY(group_id) REFERENCES group_tbl(group_id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY(user_id) REFERENCES user_tbl(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

/* ユーザテーブルコメント */
COMMENT ON TABLE user_tbl IS 'ユーザ';

COMMENT ON COLUMN user_tbl.user_id IS 'ユーザID';

COMMENT ON COLUMN user_tbl.password IS 'パスワード';

COMMENT ON COLUMN user_tbl.user_name IS 'ユーザ名';

COMMENT ON COLUMN user_tbl.error_password IS 'パスワード間違え回数';

COMMENT ON COLUMN user_tbl.lock IS 'アカウントロック';

COMMENT ON COLUMN user_tbl.authority IS '権限';

COMMENT ON COLUMN user_tbl.version IS 'バージョン';

/* TODOリストテーブルコメント */
COMMENT ON TABLE todo_tbl IS 'TODOリスト';

COMMENT ON COLUMN todo_tbl.todo_id IS 'TODOリストID';

COMMENT ON COLUMN todo_tbl.group_id IS 'グループID';

COMMENT ON COLUMN todo_tbl.todo_name IS 'TODOリスト名';

COMMENT ON COLUMN todo_tbl.todo_status IS 'TODOリスト状態';

COMMENT ON COLUMN todo_tbl.todo_memo IS 'TODOリスト値メモ';

COMMENT ON COLUMN todo_tbl.version IS 'バージョン';

/* グループテーブルコメント */
COMMENT ON TABLE group_tbl IS 'グループ';

COMMENT ON COLUMN group_tbl.group_id IS 'グループID';

COMMENT ON COLUMN group_tbl.group_name IS 'グループ名';

COMMENT ON COLUMN group_tbl.user_id IS 'ユーザID';

/* ユーザマスタ初期値 */
INSERT INTO
	user_tbl(
		user_id,
		password,
		user_name,
		error_password,
		lock,
		authority
	)
VALUES
	(
		'userTbl00000001',
		'$2a$10$m5CzxWKChQWZd464NOHLueG.sgoEfMASNwRZ6pQmN.k2wkFpiAHaS',
		'test',
		'0',
		'FALSE',
		'0'
	);

INSERT INTO
	user_tbl(
		user_id,
		password,
		user_name,
		error_password,
		lock,
		authority
	)
VALUES
	(
		'userTbl00000002',
		'$2a$10$m5CzxWKChQWZd464NOHLueG.sgoEfMASNwRZ6pQmN.k2wkFpiAHaS',
		'test',
		'0',
		'FALSE',
		'1'
	);

INSERT INTO
	group_tbl(
		group_id,
		group_name,
		user_id
	)
VALUES
	(
		'groupTbl001',
		'大掃除',
		'userTbl00000001'
	);

INSERT INTO
	group_tbl(
		group_id,
		group_name,
		user_id
	)
VALUES
	(
		'groupTbl002',
		'買い物',
		'userTbl00000001'
	);

INSERT INTO
	todo_tbl(
		todo_id,
		group_id,
		todo_name,
		todo_status,
		todo_memo,
		user_id
	)
VALUES
	(
		'todoTbl0001',
		'groupTbl001',
		'床拭き',
		false,
		'test',
		'userTbl00000001'
	);

INSERT INTO
	todo_tbl(
		todo_id,
		group_id,
		todo_name,
		todo_status,
		todo_memo,
		user_id
	)
VALUES
	(
		'todoTbl0002',
		'groupTbl001',
		'洗濯',
		true,
		'test2',
		'userTbl00000001'
	);

INSERT INTO
	todo_tbl(
		todo_id,
		group_id,
		todo_name,
		todo_status,
		todo_memo,
		user_id
	)
VALUES
	(
		'todoTbl0001',
		'groupTbl002',
		'じゃがいも',
		true,
		'～スーパー',
		'userTbl00000001'
	);

INSERT INTO
	todo_tbl(
		todo_id,
		group_id,
		todo_name,
		todo_status,
		todo_memo,
		user_id
	)
VALUES
	(
		'todoTbl0002',
		'groupTbl002',
		'もやし',
		false,
		'～スーパー',
		'userTbl00000001'
	);