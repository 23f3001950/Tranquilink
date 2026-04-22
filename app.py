from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3, os, hashlib
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'tranquilink-secret-2026'
DB_PATH = os.path.join(os.path.dirname(__file__), 'tranquilink.db')

# ════════════════════════════════════════════════════════════
#  DATABASE LAYER — two separate model classes
# ════════════════════════════════════════════════════════════

class DB:
    """Base DB helper."""
    @staticmethod
    def get():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

class CounsellorDB:
    """All counsellor-specific DB operations — keeps counsellor data isolated."""

    @staticmethod
    def create_tables(db):
        db.executescript('''
            CREATE TABLE IF NOT EXISTS counsellors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                specialisation TEXT,
                qualification TEXT,
                phone TEXT,
                bio TEXT,
                approved INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                counsellor_id INTEGER NOT NULL,
                student_id INTEGER,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT,
                is_general INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(counsellor_id) REFERENCES counsellors(id)
            );
            CREATE TABLE IF NOT EXISTS counsellor_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                counsellor_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                appointment_id INTEGER,
                rating INTEGER NOT NULL,
                review_text TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(counsellor_id) REFERENCES counsellors(id)
            );
            CREATE TABLE IF NOT EXISTS emergency_appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                counsellor_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                reason TEXT,
                status TEXT DEFAULT 'open',
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(counsellor_id) REFERENCES counsellors(id)
            );
        ''')

    @staticmethod
    def get_by_email(email):
        db = DB.get()
        c = db.execute("SELECT * FROM counsellors WHERE email=?", (email,)).fetchone()
        db.close()
        return c

    @staticmethod
    def get_by_id(cid):
        db = DB.get()
        c = db.execute("SELECT * FROM counsellors WHERE id=?", (cid,)).fetchone()
        db.close()
        return c

    @staticmethod
    def get_all_approved():
        db = DB.get()
        rows = db.execute("SELECT * FROM counsellors WHERE approved=1 ORDER BY full_name").fetchall()
        db.close()
        return rows

    @staticmethod
    def get_avg_rating(cid):
        db = DB.get()
        row = db.execute(
            "SELECT AVG(rating) as avg, COUNT(*) as cnt FROM counsellor_reviews WHERE counsellor_id=?", (cid,)
        ).fetchone()
        db.close()
        return row

    @staticmethod
    def register(full_name, email, password, specialisation, qualification, phone, bio):
        db = DB.get()
        try:
            db.execute(
                "INSERT INTO counsellors (full_name,email,password,specialisation,qualification,phone,bio) VALUES (?,?,?,?,?,?,?)",
                (full_name, email, hashlib.sha256(password.encode()).hexdigest(),
                 specialisation, qualification, phone, bio)
            )
            db.commit()
            return True, "Registration submitted. Await admin approval."
        except sqlite3.IntegrityError:
            return False, "Email already registered."
        finally:
            db.close()


# ════════════════════════════════════════════════════════════
#  DB INIT
# ════════════════════════════════════════════════════════════
def init_db():
    db = DB.get()
    db.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'student',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            counsellor_id INTEGER,
            counsellor_name TEXT,
            preferred_date TEXT,
            preferred_time TEXT,
            reason TEXT,
            status TEXT DEFAULT 'pending',
            counsellor_notes TEXT,
            is_anonymous INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            sender TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS forum_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            content TEXT,
            category TEXT,
            anonymous INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS forum_replies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            user_id INTEGER,
            counsellor_id INTEGER,
            content TEXT,
            is_counsellor INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(post_id) REFERENCES forum_posts(id)
        );
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, description TEXT, category TEXT,
            resource_type TEXT, url TEXT,
            language TEXT DEFAULT 'English',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS mood_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            mood INTEGER,
            note TEXT,
            logged_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, description TEXT, target_issue TEXT,
            start_date TEXT, end_date TEXT,
            status TEXT DEFAULT 'active',
            created_by INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    CounsellorDB.create_tables(db)

    # Seed admin
    pw = hashlib.sha256('admin123'.encode()).hexdigest()
    try:
        db.execute("INSERT INTO users (username,email,password,role) VALUES ('admin','admin@tranquilink.in',?,'admin')", (pw,))
    except: pass

    # Seed resources
    resources = [
        ('Anxiety Management Guide','Practical techniques to manage anxiety','Anxiety','guide','#','English'),
        ('Breathing Exercise Audio','5-minute guided breathing for stress relief','Stress','audio','#','English'),
        ('Depression Awareness Video','Understanding depression and seeking help','Depression','video','#','English'),
        ('Mindfulness Guide (Hindi)','Hindi mein mindfulness techniques','Mindfulness','guide','#','Hindi'),
        ('Mental Health Guide (Telugu)','Telugu lo manasika aarogya sahalalu','General','guide','#','Telugu'),
        ('Sleep Hygiene Tips','Better sleep for better mental health','Sleep','guide','#','English'),
        ('Mindfulness Meditation Audio','10-minute guided meditation session','Mindfulness','audio','#','English'),
        ('Stress Buster Video','Quick techniques to reduce academic stress','Stress','video','#','English'),
        ('Exam Anxiety Workshop','Video series on managing exam pressure','Anxiety','video','#','English'),
        ('Self-Compassion Guide','Being kind to yourself during hard times','General','guide','#','English'),
    ]
    for r in resources:
        try:
            db.execute("INSERT INTO resources (title,description,category,resource_type,url,language) VALUES (?,?,?,?,?,?)", r)
        except: pass

    # Seed forum posts
    try:
        db.execute("INSERT INTO forum_posts (user_id,title,content,category,anonymous) VALUES (1,'Dealing with exam anxiety','Feeling overwhelmed with exams. Anyone else going through this?','Anxiety',0)")
        db.execute("INSERT INTO forum_posts (user_id,title,content,category,anonymous) VALUES (1,'Tips for better sleep during finals','Sharing what has helped me sleep better during exam season...','Sleep',1)")
    except: pass

    db.commit()
    db.close()


# ════════════════════════════════════════════════════════════
#  AUTH DECORATORS
# ════════════════════════════════════════════════════════════
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session and 'counsellor_id' not in session:
            flash('Please login to continue.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def student_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'student':
            flash('This section is for students only.', 'warning')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated

def counsellor_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'counsellor':
            flash('Counsellor access required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated

def hash_pw(p):
    return hashlib.sha256(p.encode()).hexdigest()



def ai_response(msg):
    m = msg.lower()
    if any(w in m for w in ['suicide','kill myself','end my life','want to die','no reason to live']):
        return ("I'm deeply concerned. Please reach out immediately — iCall: <strong>9152987821</strong> (Mon-Sat 8am-10pm) or Vandrevala Foundation: <strong>1860-2662-345</strong> (24/7). You matter. Would you like me to help you book an emergency counsellor appointment?", True)
    if any(w in m for w in ['self harm','hurt myself','cutting','harm myself']):
        return ("It sounds like you're in a lot of pain. Please speak with a counsellor — you don't have to face this alone. iCall: <strong>9152987821</strong>. Shall I help you book a confidential appointment?", True)
    if any(w in m for w in ['anxious','anxiety','panic','scared','nervous']):
        return ("Anxiety can feel overwhelming but it is manageable. Try 4-7-8 breathing: inhale for 4 counts, hold for 7, exhale for 8. Also name 5 things you can see right now — this grounds you. 🌿 Want more strategies or to speak with a counsellor?", False)
    if any(w in m for w in ['depressed','depression','sad','hopeless','empty','worthless']):
        return ("I hear you, and your feelings are completely valid. Depression is real and treatable. Small steps matter: a short walk, journalling, talking to someone. Our counsellors are here for you. Want to book a confidential session? 💙", False)
    if any(w in m for w in ['stress','stressed','exam','assignment','deadline','pressure']):
        return ("Academic pressure is real. Try the Pomodoro method: 25 min focused work, 5 min break. Break tasks into tiny steps. Your worth is NOT your grades. 📚 Check the Resource Hub for stress-relief audio!", False)
    if any(w in m for w in ['sleep','insomnia','cant sleep','tired','exhausted']):
        return ("Poor sleep affects everything. Try: no screens 1 hr before bed, consistent sleep times, a short breathing exercise. Our Resource Hub has sleep hygiene guides!", False)
    if any(w in m for w in ['lonely','alone','isolated','no friends']):
        return ("Loneliness on campus is more common than you think. Our Peer Support Forum connects you with peers who understand. You belong here. 💙", False)
    if any(w in m for w in ['appointment','book','counsellor','session']):
        return ("Head to the <a href='/appointments'>Booking section</a> to schedule a confidential session with a counsellor. All sessions are private and judgment-free.", False)
    if any(w in m for w in ['exercise','practice','activity','routine']):
        return ("Our counsellors suggest personalised exercises for students. Check the <a href='/exercises'>Exercises section</a> for routines recommended by professionals!", False)
    if any(w in m for w in ['hello','hi','hey','namaste']):
        return ("Hello! 👋 I'm TranquilBot, your mental wellness companion. How are you feeling today? I'm here to listen and help.", False)
    if any(w in m for w in ['thank','thanks']):
        return ("You're very welcome. Reaching out is a sign of strength. Take care of yourself. 💙", False)
    return ("Thank you for sharing. Could you tell me more about what you're going through? I can suggest coping strategies, share resources, or help you connect with a counsellor. 💙", False)


# ════════════════════════════════════════════════════════════
#  PUBLIC ROUTES
# ════════════════════════════════════════════════════════════
@app.route('/')
def index():
    counsellors = CounsellorDB.get_all_approved()
    return render_template('index.html', counsellors=counsellors)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = hash_pw(request.form['password'])
        db = DB.get()
        try:
            db.execute("INSERT INTO users (username,email,password) VALUES (?,?,?)", (username,email,password))
            db.commit()
            flash('Account created! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists.', 'danger')
        finally:
            db.close()
    return render_template('register.html')

@app.route('/counsellor/register', methods=['GET','POST'])
def counsellor_register():
    if request.method == 'POST':
        ok, msg = CounsellorDB.register(
            request.form['full_name'].strip(),
            request.form['email'].strip(),
            request.form['password'],
            request.form['specialisation'],
            request.form['qualification'],
            request.form['phone'],
            request.form['bio']
        )
        flash(msg, 'success' if ok else 'danger')
        if ok:
            return redirect(url_for('login'))
    return render_template('counsellor_register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = hash_pw(request.form['password'])
        login_as = request.form.get('login_as', 'student')

        if login_as == 'counsellor':
            c = DB.get().execute("SELECT * FROM counsellors WHERE email=? AND password=?", (email,password)).fetchone()
            if c:
                if not c['approved']:
                    flash('Your account is pending admin approval.', 'warning')
                    return redirect(url_for('login'))
                session['counsellor_id'] = c['id']
                session['username'] = c['full_name']
                session['role'] = 'counsellor'
                flash(f'Welcome, {c["full_name"]}!', 'success')
                return redirect(url_for('counsellor_dashboard'))
            flash('Invalid counsellor credentials.', 'danger')
        else:
            db = DB.get()
            user = db.execute("SELECT * FROM users WHERE email=? AND password=?", (email,password)).fetchone()
            db.close()
            if user:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                flash(f'Welcome back, {user["username"]}!', 'success')
                if user['role'] == 'admin':
                    return redirect(url_for('admin_dashboard'))
                return redirect(url_for('dashboard'))
            flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/resources')
def resources():
    db = DB.get()
    category = request.args.get('category','')
    lang = request.args.get('lang','')
    rtype = request.args.get('type','')
    query = "SELECT * FROM resources WHERE 1=1"
    params = []
    if category: query += " AND category=?"; params.append(category)
    if lang:     query += " AND language=?"; params.append(lang)
    if rtype:    query += " AND resource_type=?"; params.append(rtype)
    res = db.execute(query, params).fetchall()
    categories = [r[0] for r in db.execute("SELECT DISTINCT category FROM resources").fetchall()]
    languages  = [r[0] for r in db.execute("SELECT DISTINCT language FROM resources").fetchall()]
    db.close()
    return render_template('resources.html', resources=res, categories=categories,
                           languages=languages, selected_cat=category,
                           selected_lang=lang, selected_type=rtype)


# ════════════════════════════════════════════════════════════
#  STUDENT ROUTES
# ════════════════════════════════════════════════════════════
@app.route('/dashboard')
@login_required
def dashboard():
    if session.get('role') == 'counsellor':
        return redirect(url_for('counsellor_dashboard'))
    if session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    db = DB.get()
    appts = db.execute(
        "SELECT a.*, c.full_name as c_name FROM appointments a LEFT JOIN counsellors c ON a.counsellor_id=c.id WHERE a.user_id=? ORDER BY a.created_at DESC LIMIT 3",
        (session['user_id'],)
    ).fetchall()
    mood = db.execute("SELECT * FROM mood_logs WHERE user_id=? ORDER BY logged_at DESC LIMIT 7", (session['user_id'],)).fetchall()
    exercises = db.execute(
        "SELECT e.*, c.full_name as c_name FROM exercises e JOIN counsellors c ON e.counsellor_id=c.id WHERE e.student_id=? OR e.is_general=1 ORDER BY e.created_at DESC LIMIT 5",
        (session['user_id'],)
    ).fetchall()
    db.close()
    return render_template('dashboard.html', appointments=appts, mood_logs=mood, exercises=exercises)

@app.route('/mood', methods=['POST'])
@login_required
@student_required
def log_mood():
    db = DB.get()
    db.execute("INSERT INTO mood_logs (user_id,mood,note) VALUES (?,?,?)",
               (session['user_id'], int(request.form['mood']), request.form.get('note','')))
    db.commit()
    db.close()
    flash('Mood logged! 💙', 'success')
    return redirect(url_for('dashboard'))

@app.route('/chat')
@login_required
@student_required
def chat():
    db = DB.get()
    messages = db.execute("SELECT * FROM chat_messages WHERE user_id=? ORDER BY created_at ASC LIMIT 50", (session['user_id'],)).fetchall()
    db.close()
    return render_template('chat.html', messages=messages)

@app.route('/chat/send', methods=['POST'])
@login_required
@student_required
def chat_send():
    data = request.get_json()
    msg = data.get('message','').strip()
    if not msg:
        return jsonify({'error':'Empty'}), 400
    db = DB.get()
    db.execute("INSERT INTO chat_messages (user_id,message,sender) VALUES (?,?,'user')", (session['user_id'],msg))
    reply, urgent = ai_response(msg)
    db.execute("INSERT INTO chat_messages (user_id,message,sender) VALUES (?,?,'bot')", (session['user_id'],reply))
    db.commit()
    db.close()
    return jsonify({'reply': reply, 'urgent': urgent})

@app.route('/appointments', methods=['GET','POST'])
@login_required
@student_required
def appointments():
    db = DB.get()
    counsellors = CounsellorDB.get_all_approved()
    if request.method == 'POST':
        cid = request.form.get('counsellor_id') or None
        cname = ''
        if cid:
            c = CounsellorDB.get_by_id(cid)
            cname = c['full_name'] if c else ''
        db.execute(
            "INSERT INTO appointments (user_id,counsellor_id,counsellor_name,preferred_date,preferred_time,reason,is_anonymous) VALUES (?,?,?,?,?,?,?)",
            (session['user_id'], cid, cname, request.form['preferred_date'],
             request.form['preferred_time'], request.form['reason'],
             1 if request.form.get('anonymous') else 0)
        )
        db.commit()
        flash('Appointment requested! You will be contacted to confirm.', 'success')
        return redirect(url_for('appointments'))
    appts = db.execute(
        "SELECT a.*, c.full_name as c_name FROM appointments a LEFT JOIN counsellors c ON a.counsellor_id=c.id WHERE a.user_id=? ORDER BY a.created_at DESC",
        (session['user_id'],)
    ).fetchall()
    db.close()
    return render_template('appointments.html', appointments=appts, counsellors=counsellors)

@app.route('/exercises')
@login_required
@student_required
def exercises():
    db = DB.get()
    exs = db.execute(
        "SELECT e.*, c.full_name as c_name FROM exercises e JOIN counsellors c ON e.counsellor_id=c.id WHERE e.student_id=? OR e.is_general=1 ORDER BY e.created_at DESC",
        (session['user_id'],)
    ).fetchall()
    db.close()
    return render_template('exercises.html', exercises=exs)

@app.route('/forum')
@login_required
def forum():
    if session.get('role') == 'admin':
        flash('Admins cannot access the forum.', 'warning')
        return redirect(url_for('admin_dashboard'))
    db = DB.get()
    posts = db.execute("""
        SELECT fp.*, u.username,
        (SELECT COUNT(*) FROM forum_replies WHERE post_id=fp.id) as reply_count
        FROM forum_posts fp JOIN users u ON fp.user_id=u.id
        WHERE fp.status='active' ORDER BY fp.created_at DESC
    """).fetchall()
    db.close()
    return render_template('forum.html', posts=posts)

@app.route('/forum/new', methods=['GET','POST'])
@login_required
@student_required
def new_post():
    if request.method == 'POST':
        db = DB.get()
        db.execute(
            "INSERT INTO forum_posts (user_id,title,content,category,anonymous) VALUES (?,?,?,?,?)",
            (session['user_id'], request.form['title'], request.form['content'],
             request.form['category'], 1 if request.form.get('anonymous') else 0)
        )
        db.commit()
        db.close()
        flash('Post shared with the community!', 'success')
        return redirect(url_for('forum'))
    return render_template('new_post.html')

@app.route('/forum/post/<int:post_id>', methods=['GET','POST'])
@login_required
def view_post(post_id):
    if session.get('role') == 'admin':
        flash('Admins cannot access the forum.', 'warning')
        return redirect(url_for('admin_dashboard'))
    db = DB.get()
    post = db.execute("SELECT fp.*,u.username FROM forum_posts fp JOIN users u ON fp.user_id=u.id WHERE fp.id=?", (post_id,)).fetchone()
    if not post:
        flash('Post not found.','danger'); return redirect(url_for('forum'))
    if request.method == 'POST':
        is_c = 1 if session.get('role') == 'counsellor' else 0
        cid  = session.get('counsellor_id') if is_c else None
        db.execute(
            "INSERT INTO forum_replies (post_id,user_id,counsellor_id,content,is_counsellor) VALUES (?,?,?,?,?)",
            (post_id,
             session.get('user_id'),
             cid,
             request.form['content'],
             is_c)
        )
        db.commit()
        flash('Reply posted!', 'success')
        return redirect(url_for('view_post', post_id=post_id))
    replies = db.execute("""
        SELECT fr.*,
               COALESCE(u.username, c.full_name) as display_name
        FROM forum_replies fr
        LEFT JOIN users u ON fr.user_id=u.id AND fr.is_counsellor=0
        LEFT JOIN counsellors c ON fr.counsellor_id=c.id AND fr.is_counsellor=1
        WHERE fr.post_id=? ORDER BY fr.created_at ASC
    """, (post_id,)).fetchall()
    db.close()
    return render_template('view_post.html', post=post, replies=replies)

# ── Review a counsellor (student) ──────────────────────────────────────────
@app.route('/counsellor/<int:cid>/review', methods=['GET','POST'])
@login_required
@student_required
def review_counsellor(cid):
    c = CounsellorDB.get_by_id(cid)
    if not c:
        flash('Counsellor not found.','danger')
        return redirect(url_for('appointments'))
    db = DB.get()
    if request.method == 'POST':
        appt_id = request.form.get('appointment_id') or None
        db.execute(
            "INSERT INTO counsellor_reviews (counsellor_id,student_id,appointment_id,rating,review_text) VALUES (?,?,?,?,?)",
            (cid, session['user_id'], appt_id, int(request.form['rating']), request.form['review_text'])
        )
        db.commit()
        flash('Review submitted! Thank you. 💙', 'success')
        db.close()
        return redirect(url_for('appointments'))
    appts = db.execute(
        "SELECT * FROM appointments WHERE user_id=? AND counsellor_id=? AND status='completed'",
        (session['user_id'], cid)
    ).fetchall()
    db.close()
    return render_template('review_counsellor.html', counsellor=c, appointments=appts)


# ════════════════════════════════════════════════════════════
#  COUNSELLOR ROUTES
# ════════════════════════════════════════════════════════════
@app.route('/counsellor/dashboard')
@login_required
@counsellor_required
def counsellor_dashboard():
    cid = session['counsellor_id']
    db = DB.get()
    appts = db.execute(
        "SELECT a.*, u.username, u.email FROM appointments a JOIN users u ON a.user_id=u.id WHERE a.counsellor_id=? ORDER BY a.preferred_date ASC",
        (cid,)
    ).fetchall()
    pending = [a for a in appts if a['status'] == 'pending']
    emergency = db.execute(
        "SELECT ea.*, u.username FROM emergency_appointments ea JOIN users u ON ea.student_id=u.id WHERE ea.counsellor_id=? ORDER BY ea.created_at DESC",
        (cid,)
    ).fetchall()
    reviews = db.execute(
        "SELECT cr.*, u.username FROM counsellor_reviews cr JOIN users u ON cr.student_id=u.id WHERE cr.counsellor_id=? ORDER BY cr.created_at DESC",
        (cid,)
    ).fetchall()
    stats = CounsellorDB.get_avg_rating(cid)
    exercises = db.execute("SELECT * FROM exercises WHERE counsellor_id=? ORDER BY created_at DESC LIMIT 5", (cid,)).fetchall()
    db.close()
    return render_template('counsellor_dashboard.html', appointments=appts,
                           pending=pending, emergency=emergency,
                           reviews=reviews, stats=stats, exercises=exercises)

@app.route('/counsellor/appointments')
@login_required
@counsellor_required
def counsellor_appointments():
    cid = session['counsellor_id']
    db = DB.get()
    appts = db.execute(
        "SELECT a.*, u.username, u.email FROM appointments a JOIN users u ON a.user_id=u.id WHERE a.counsellor_id=? ORDER BY a.preferred_date DESC",
        (cid,)
    ).fetchall()
    db.close()
    return render_template('counsellor_appointments.html', appointments=appts)

@app.route('/counsellor/appointment/<int:appt_id>/update', methods=['POST'])
@login_required
@counsellor_required
def counsellor_update_appt(appt_id):
    db = DB.get()
    db.execute(
        "UPDATE appointments SET status=?, counsellor_notes=? WHERE id=? AND counsellor_id=?",
        (request.form['status'], request.form.get('notes',''), appt_id, session['counsellor_id'])
    )
    db.commit()
    db.close()
    flash('Appointment updated.', 'success')
    return redirect(url_for('counsellor_appointments'))

@app.route('/counsellor/emergency', methods=['GET','POST'])
@login_required
@counsellor_required
def counsellor_emergency():
    cid = session['counsellor_id']
    db = DB.get()
    if request.method == 'POST':
        db.execute(
            "INSERT INTO emergency_appointments (counsellor_id,student_id,reason,notes) VALUES (?,?,?,?)",
            (cid, request.form['student_id'], request.form['reason'], request.form.get('notes',''))
        )
        db.commit()
        flash('Emergency appointment created.', 'success')
        return redirect(url_for('counsellor_emergency'))
    emergencies = db.execute(
        "SELECT ea.*, u.username FROM emergency_appointments ea JOIN users u ON ea.student_id=u.id WHERE ea.counsellor_id=? ORDER BY ea.created_at DESC",
        (cid,)
    ).fetchall()
    students = db.execute("SELECT id, username, email FROM users WHERE role='student' ORDER BY username").fetchall()
    db.close()
    return render_template('counsellor_emergency.html', emergencies=emergencies, students=students)

@app.route('/counsellor/emergency/<int:eid>/close', methods=['POST'])
@login_required
@counsellor_required
def close_emergency(eid):
    db = DB.get()
    db.execute("UPDATE emergency_appointments SET status='closed' WHERE id=? AND counsellor_id=?",
               (eid, session['counsellor_id']))
    db.commit()
    db.close()
    flash('Emergency appointment closed.', 'success')
    return redirect(url_for('counsellor_emergency'))

@app.route('/counsellor/exercises', methods=['GET','POST'])
@login_required
@counsellor_required
def counsellor_exercises():
    cid = session['counsellor_id']
    db = DB.get()
    if request.method == 'POST':
        student_id = request.form.get('student_id') or None
        is_general = 1 if not student_id else 0
        db.execute(
            "INSERT INTO exercises (counsellor_id,student_id,title,description,category,is_general) VALUES (?,?,?,?,?,?)",
            (cid, student_id, request.form['title'], request.form['description'], request.form['category'], is_general)
        )
        db.commit()
        flash('Exercise added!', 'success')
        return redirect(url_for('counsellor_exercises'))
    exercises = db.execute(
        "SELECT e.*, CASE WHEN e.student_id IS NULL THEN 'All Students' ELSE u.username END as target FROM exercises e LEFT JOIN users u ON e.student_id=u.id WHERE e.counsellor_id=? ORDER BY e.created_at DESC",
        (cid,)
    ).fetchall()
    students = db.execute("SELECT id,username FROM users WHERE role='student' ORDER BY username").fetchall()
    db.close()
    return render_template('counsellor_exercises.html', exercises=exercises, students=students)

@app.route('/counsellor/reviews')
@login_required
@counsellor_required
def counsellor_reviews():
    cid = session['counsellor_id']
    db = DB.get()
    reviews = db.execute(
        "SELECT cr.*, u.username FROM counsellor_reviews cr JOIN users u ON cr.student_id=u.id WHERE cr.counsellor_id=? ORDER BY cr.created_at DESC",
        (cid,)
    ).fetchall()
    stats = CounsellorDB.get_avg_rating(cid)
    db.close()
    return render_template('counsellor_reviews.html', reviews=reviews, stats=stats)

@app.route('/counsellor/forum')
@login_required
@counsellor_required
def counsellor_forum():
    return redirect(url_for('forum'))


# ════════════════════════════════════════════════════════════
#  ADMIN ROUTES
# ════════════════════════════════════════════════════════════
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    db = DB.get()
    stats = {
        'total_students': db.execute("SELECT COUNT(*) FROM users WHERE role='student'").fetchone()[0],
        'total_counsellors': db.execute("SELECT COUNT(*) FROM counsellors WHERE approved=1").fetchone()[0],
        'pending_counsellors': db.execute("SELECT COUNT(*) FROM counsellors WHERE approved=0").fetchone()[0],
        'total_appointments': db.execute("SELECT COUNT(*) FROM appointments").fetchone()[0],
        'pending_appointments': db.execute("SELECT COUNT(*) FROM appointments WHERE status='pending'").fetchone()[0],
        'total_posts': db.execute("SELECT COUNT(*) FROM forum_posts").fetchone()[0],
        'chat_sessions': db.execute("SELECT COUNT(DISTINCT user_id) FROM chat_messages").fetchone()[0],
        'mood_entries': db.execute("SELECT COUNT(*) FROM mood_logs").fetchone()[0],
        'active_campaigns': db.execute("SELECT COUNT(*) FROM campaigns WHERE status='active'").fetchone()[0],
        'emergencies_open': db.execute("SELECT COUNT(*) FROM emergency_appointments WHERE status='open'").fetchone()[0],
    }
    mood_data    = [dict(r) for r in db.execute("SELECT mood, COUNT(*) as cnt FROM mood_logs GROUP BY mood ORDER BY mood").fetchall()]
    cat_data     = [dict(r) for r in db.execute("SELECT category, COUNT(*) as cnt FROM forum_posts GROUP BY category").fetchall()]
    weekly       = [dict(r) for r in db.execute("SELECT DATE(logged_at) as day, AVG(mood) as avg_mood FROM mood_logs GROUP BY DATE(logged_at) ORDER BY day DESC LIMIT 7").fetchall()]
    appts        = db.execute("SELECT a.*, CASE WHEN a.is_anonymous=1 THEN 'Anonymous' ELSE u.username END as dname, COALESCE(c.full_name,'—') as cname FROM appointments a JOIN users u ON a.user_id=u.id LEFT JOIN counsellors c ON a.counsellor_id=c.id ORDER BY a.created_at DESC LIMIT 10").fetchall()
    pending_c    = db.execute("SELECT * FROM counsellors WHERE approved=0 ORDER BY created_at DESC").fetchall()
    campaigns    = db.execute("SELECT * FROM campaigns ORDER BY created_at DESC LIMIT 3").fetchall()
    db.close()
    return render_template('admin.html', stats=stats, mood_data=mood_data,
                           cat_data=cat_data, weekly=weekly, appointments=appts,
                           pending_counsellors=pending_c, campaigns=campaigns)

@app.route('/admin/counsellor/<int:cid>/approve', methods=['POST'])
@login_required
@admin_required
def approve_counsellor(cid):
    db = DB.get()
    db.execute("UPDATE counsellors SET approved=1 WHERE id=?", (cid,))
    db.commit()
    db.close()
    flash('Counsellor approved!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/counsellor/<int:cid>/reject', methods=['POST'])
@login_required
@admin_required
def reject_counsellor(cid):
    db = DB.get()
    db.execute("DELETE FROM counsellors WHERE id=?", (cid,))
    db.commit()
    db.close()
    flash('Counsellor registration rejected and removed.', 'warning')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/appointment/<int:appt_id>/update', methods=['POST'])
@login_required
@admin_required
def update_appointment(appt_id):
    db = DB.get()
    db.execute("UPDATE appointments SET status=? WHERE id=?", (request.form['status'], appt_id))
    db.commit()
    db.close()
    flash('Appointment status updated.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/campaigns', methods=['GET','POST'])
@login_required
@admin_required
def admin_campaigns():
    db = DB.get()
    if request.method == 'POST':
        db.execute(
            "INSERT INTO campaigns (title,description,target_issue,start_date,end_date,created_by) VALUES (?,?,?,?,?,?)",
            (request.form['title'], request.form['description'], request.form['target_issue'],
             request.form['start_date'], request.form['end_date'], session['user_id'])
        )
        db.commit()
        flash('Campaign launched!', 'success')
        return redirect(url_for('admin_campaigns'))
    campaigns = db.execute("SELECT * FROM campaigns ORDER BY created_at DESC").fetchall()
    top_cats  = [dict(r) for r in db.execute("SELECT category, COUNT(*) as cnt FROM forum_posts GROUP BY category ORDER BY cnt DESC LIMIT 5").fetchall()]
    low_moods = db.execute("SELECT COUNT(*) FROM mood_logs WHERE mood <= 2").fetchone()[0]
    total_m   = db.execute("SELECT COUNT(*) FROM mood_logs").fetchone()[0]
    db.close()
    return render_template('campaigns.html', campaigns=campaigns, top_forum_cats=top_cats,
                           low_mood_pct=round(low_moods/total_m*100) if total_m else 0)

@app.route('/admin/campaigns/<int:cid>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_campaign(cid):
    db = DB.get()
    cur = db.execute("SELECT status FROM campaigns WHERE id=?", (cid,)).fetchone()
    new = 'inactive' if cur and cur['status']=='active' else 'active'
    db.execute("UPDATE campaigns SET status=? WHERE id=?", (new, cid))
    db.commit()
    db.close()
    flash(f'Campaign {"activated" if new=="active" else "deactivated"}.', 'success')
    return redirect(url_for('admin_campaigns'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5050)
