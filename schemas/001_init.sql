CREATE TABLE IF NOT EXISTS admins (
    employee_id TEXT PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    branch TEXT,
    auth_token TEXT,
    profile_picture TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sessions (
    session_num INTEGER PRIMARY KEY,
    year INTEGER
);

CREATE TABLE IF NOT EXISTS stuadmn (
    id SERIAL PRIMARY KEY,
    session_num INTEGER NOT NULL,
    reg_no TEXT NOT NULL,
    data JSONB NOT NULL,
    UNIQUE(session_num, reg_no)
);

CREATE TABLE IF NOT EXISTS formrecv (
    id SERIAL PRIMARY KEY,
    session_num INTEGER NOT NULL,
    reg_no TEXT NOT NULL,
    data JSONB NOT NULL,
    UNIQUE(session_num, reg_no)
);

CREATE TABLE IF NOT EXISTS reenroll (
    id SERIAL PRIMARY KEY,
    session_num INTEGER NOT NULL,
    reg_no TEXT NOT NULL,
    data JSONB NOT NULL,
    UNIQUE(session_num, reg_no)
);

CREATE TABLE IF NOT EXISTS receipt (
    id SERIAL PRIMARY KEY,
    session_num INTEGER NOT NULL,
    reg_no TEXT NOT NULL,
    data JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS marks (
    id SERIAL PRIMARY KEY,
    session_num INTEGER NOT NULL,
    reg_no TEXT NOT NULL,
    data JSONB NOT NULL,
    UNIQUE(session_num, reg_no)
);

CREATE TABLE IF NOT EXISTS instreg (
    id SERIAL PRIMARY KEY,
    session_num INTEGER NOT NULL,
    reg_no TEXT NOT NULL,
    data JSONB NOT NULL,
    UNIQUE(session_num, reg_no)
);

CREATE INDEX IF NOT EXISTS idx_formrecv_name ON formrecv ((data->>'name'));
CREATE INDEX IF NOT EXISTS idx_formrecv_reg ON formrecv (reg_no);
CREATE INDEX IF NOT EXISTS idx_receipt_reg ON receipt (reg_no);

CREATE TABLE IF NOT EXISTS branches (
    branch_code TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS branch_sessions (
    branch_code TEXT NOT NULL REFERENCES branches(branch_code) ON DELETE CASCADE,
    session_num INTEGER NOT NULL,
    PRIMARY KEY (branch_code, session_num)
);

CREATE TABLE IF NOT EXISTS batch (
    id BIGSERIAL PRIMARY KEY,
    branch_code TEXT NOT NULL,
    session_num INTEGER NOT NULL,
    batchcode TEXT,
    coursecode TEXT,
    courseid TEXT,
    batchday TEXT,
    batchtime TEXT,
    faculty TEXT,
    totalseat TEXT,
    alloted TEXT,
    classstart TEXT,
    terget TEXT,
    remarks TEXT,
    session TEXT,
    ses_half TEXT,
    centre TEXT,
    deleted TEXT,
    user_name TEXT,
    FOREIGN KEY (branch_code, session_num)
        REFERENCES branch_sessions (branch_code, session_num)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS examtime (
    id BIGSERIAL PRIMARY KEY,
    branch_code TEXT NOT NULL,
    session_num INTEGER NOT NULL,
    rollno TEXT,
    reg_no TEXT,
    time TEXT,
    date TEXT,
    lab TEXT,
    batch TEXT,
    batch1 TEXT,
    term TEXT,
    session TEXT,
    ses_half TEXT,
    centre TEXT,
    user_name TEXT,
    remarks TEXT,
    FOREIGN KEY (branch_code, session_num)
        REFERENCES branch_sessions (branch_code, session_num)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS formrecv_hier (
    id BIGSERIAL PRIMARY KEY,
    branch_code TEXT NOT NULL,
    session_num INTEGER NOT NULL,
    form_no TEXT,
    recv_date TEXT,
    name TEXT,
    dob TEXT,
    sex TEXT,
    caste TEXT,
    f_name TEXT,
    add_1 TEXT,
    add_2 TEXT,
    po TEXT,
    district TEXT,
    pin TEXT,
    phone TEXT,
    mobile TEXT,
    gq1 TEXT,
    gq2 TEXT,
    gq3 TEXT,
    gq4 TEXT,
    tq TEXT,
    course_id TEXT,
    centre_id TEXT,
    reg_no TEXT,
    scholar TEXT,
    session TEXT,
    ses_half TEXT,
    remarks TEXT,
    horemarks TEXT,
    semister TEXT,
    otheryctc TEXT,
    frontline TEXT,
    attend_by TEXT,
    user_name TEXT,
    prospectusissued TEXT,
    checkdob TEXT,
    checkcaste TEXT,
    checkgq1 TEXT,
    checkgq2 TEXT,
    checkgq3 TEXT,
    checkgq4 TEXT,
    checktq TEXT,
    aadharno TEXT,
    employername TEXT,
    employeradd TEXT,
    designame TEXT,
    actualsalary TEXT,
    jobjoindate TEXT,
    jobportaldate TEXT,
    salaryrem TEXT,
    e_mail TEXT,
    next_session TEXT,
    re_exam TEXT,
    exam_appear TEXT,
    FOREIGN KEY (branch_code, session_num)
        REFERENCES branch_sessions (branch_code, session_num)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS icardbookissue (
    id BIGSERIAL PRIMARY KEY,
    branch_code TEXT NOT NULL,
    session_num INTEGER NOT NULL,
    reg_no TEXT,
    name TEXT,
    batch TEXT,
    icard TEXT,
    book1 TEXT,
    book2 TEXT,
    book3 TEXT,
    book4 TEXT,
    centrename TEXT,
    user_name TEXT,
    FOREIGN KEY (branch_code, session_num)
        REFERENCES branch_sessions (branch_code, session_num)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS instreg_hier (
    id BIGSERIAL PRIMARY KEY,
    branch_code TEXT NOT NULL,
    session_num INTEGER NOT NULL,
    reg_no TEXT,
    admission TEXT,
    admn_recpt TEXT,
    inst_1_due TEXT,
    inst_1_dt TEXT,
    i_1_recpt TEXT,
    inst_2_due TEXT,
    inst_2_dt TEXT,
    i_2_recpt TEXT,
    inst_3_due TEXT,
    inst_3_dt TEXT,
    i_3_recpt TEXT,
    inst_4_due TEXT,
    inst_4_dt TEXT,
    i_4_recpt TEXT,
    inst_5_due TEXT,
    inst_5_dt TEXT,
    i_5_recpt TEXT,
    inst_6_due TEXT,
    inst_6_dt TEXT,
    i_6_recpt TEXT,
    inst_7_due TEXT,
    inst_7_dt TEXT,
    i_7_recpt TEXT,
    inst_8_due TEXT,
    inst_8_dt TEXT,
    i_8_recpt TEXT,
    session TEXT,
    ses_half TEXT,
    centre_id TEXT,
    sem_payabl TEXT,
    sem_paypart TEXT,
    user_name TEXT,
    FOREIGN KEY (branch_code, session_num)
        REFERENCES branch_sessions (branch_code, session_num)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS letter (
    id BIGSERIAL PRIMARY KEY,
    branch_code TEXT NOT NULL,
    session_num INTEGER NOT NULL,
    reference TEXT,
    srl TEXT,
    reg_no TEXT,
    name TEXT,
    "lateral" TEXT,
    course TEXT,
    batch TEXT,
    date TEXT,
    time TEXT,
    reminder TEXT,
    sender TEXT,
    remarks TEXT,
    faculty TEXT,
    centre TEXT,
    session TEXT,
    user_name TEXT,
    deleted TEXT,
    FOREIGN KEY (branch_code, session_num)
        REFERENCES branch_sessions (branch_code, session_num)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS marks_hier (
    id BIGSERIAL PRIMARY KEY,
    branch_code TEXT NOT NULL,
    session_num INTEGER NOT NULL,
    reg_no TEXT,
    batch_code TEXT,
    p1s1 TEXT,
    p2s1 TEXT,
    p3s1 TEXT,
    ts1 TEXT,
    as1 TEXT,
    gs1 TEXT,
    p1s2 TEXT,
    p2s2 TEXT,
    ts2 TEXT,
    as2 TEXT,
    gs2 TEXT,
    p1s3 TEXT,
    p2s3 TEXT,
    ts3 TEXT,
    as3 TEXT,
    gs3 TEXT,
    tot TEXT,
    avg TEXT,
    grade TEXT,
    centre TEXT,
    pre_reg_no TEXT,
    session TEXT,
    certi_no TEXT,
    certi_date TEXT,
    trans_no TEXT,
    trans_date TEXT,
    user_name TEXT,
    remarks TEXT,
    exam_appear TEXT,
    FOREIGN KEY (branch_code, session_num)
        REFERENCES branch_sessions (branch_code, session_num)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS receipt_hier (
    id BIGSERIAL PRIMARY KEY,
    branch_code TEXT NOT NULL,
    session_num INTEGER NOT NULL,
    recpnopre TEXT,
    cnt_prefix TEXT,
    receiptno TEXT,
    recptdate TEXT,
    recpttime TEXT,
    amount TEXT,
    coursefees TEXT,
    admnfees TEXT,
    prospectus TEXT,
    batchchang TEXT,
    fine_amt TEXT,
    fine_days TEXT,
    instalment TEXT,
    reg_no TEXT,
    recpt_type TEXT,
    pay_mode TEXT,
    dd_no TEXT,
    dd_dt TEXT,
    draw_bank TEXT,
    remarks TEXT,
    "lateral" TEXT,
    centre_id TEXT,
    session TEXT,
    ses_half TEXT,
    frontline TEXT,
    user_name TEXT,
    deleted TEXT,
    dd_no_2 TEXT,
    FOREIGN KEY (branch_code, session_num)
        REFERENCES branch_sessions (branch_code, session_num)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reenroll_hier (
    id BIGSERIAL PRIMARY KEY,
    branch_code TEXT NOT NULL,
    session_num INTEGER NOT NULL,
    reg_no TEXT,
    batchcode TEXT,
    "lateral" TEXT,
    course_ap1 TEXT,
    course_ap2 TEXT,
    course_ap3 TEXT,
    n_reg_no_1 TEXT,
    course_ad1 TEXT,
    batch_no_1 TEXT,
    n_reg_no_2 TEXT,
    course_ad2 TEXT,
    batch_no_2 TEXT,
    n_reg_no_3 TEXT,
    course_ad3 TEXT,
    batch_no_3 TEXT,
    session TEXT,
    ses_half TEXT,
    already_dip TEXT,
    centre TEXT,
    user_name TEXT,
    FOREIGN KEY (branch_code, session_num)
        REFERENCES branch_sessions (branch_code, session_num)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS scholarlist (
    id BIGSERIAL PRIMARY KEY,
    branch_code TEXT NOT NULL,
    session_num INTEGER NOT NULL,
    reg_no TEXT,
    course TEXT,
    batch TEXT,
    scholarsem TEXT,
    voucherno TEXT,
    voucherdate TEXT,
    amount TEXT,
    returndate TEXT,
    isreturned TEXT,
    centre TEXT,
    user_name TEXT,
    FOREIGN KEY (branch_code, session_num)
        REFERENCES branch_sessions (branch_code, session_num)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS stuadmn_hier (
    id BIGSERIAL PRIMARY KEY,
    branch_code TEXT NOT NULL,
    session_num INTEGER NOT NULL,
    reg_no TEXT,
    name TEXT,
    f_name TEXT,
    course_id TEXT,
    batch TEXT,
    payday TEXT,
    form_no TEXT,
    pre_reg TEXT,
    centre_id TEXT,
    "lateral" TEXT,
    final_roll TEXT,
    remarks TEXT,
    session TEXT,
    ses_half TEXT,
    on_mid TEXT,
    on_final TEXT,
    scholar TEXT,
    semister TEXT,
    otheryctc TEXT,
    frontline TEXT,
    user_name TEXT,
    next_session TEXT,
    re_exam TEXT,
    exam_loginid TEXT,
    exam_password TEXT,
    exam_appear TEXT,
    exam_reg_on TEXT,
    exam_reg_by TEXT,
    exam_schedule TEXT,
    FOREIGN KEY (branch_code, session_num)
        REFERENCES branch_sessions (branch_code, session_num)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_examtime_reg_no ON examtime (reg_no);
CREATE INDEX IF NOT EXISTS idx_formrecv_hier_reg_no ON formrecv_hier (reg_no);
CREATE INDEX IF NOT EXISTS idx_icardbookissue_reg_no ON icardbookissue (reg_no);
CREATE INDEX IF NOT EXISTS idx_instreg_hier_reg_no ON instreg_hier (reg_no);
CREATE INDEX IF NOT EXISTS idx_letter_reg_no ON letter (reg_no);
CREATE INDEX IF NOT EXISTS idx_marks_hier_reg_no ON marks_hier (reg_no);
CREATE INDEX IF NOT EXISTS idx_receipt_hier_reg_no ON receipt_hier (reg_no);
CREATE INDEX IF NOT EXISTS idx_reenroll_hier_reg_no ON reenroll_hier (reg_no);
CREATE INDEX IF NOT EXISTS idx_scholarlist_reg_no ON scholarlist (reg_no);
CREATE INDEX IF NOT EXISTS idx_stuadmn_hier_reg_no ON stuadmn_hier (reg_no);

-- Placeholder: insert branches available in the root folder list.
-- Example:
-- INSERT INTO branches (branch_code) VALUES ('N24'), ('M32');
