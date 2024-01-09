from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg2
from connect import get_db_connection

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッションを安全に保つためのシークレットキー

@app.route('/')
def Home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM Users WHERE name = %s AND password = %s', (username, password))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            session['user_id'] = user[0]  # user_id をセッションに保存
            session['username'] = username  # ユーザー名をセッションに保存
            return redirect(url_for('home'))
        else:
            flash('ユーザー名またはパスワードが間違っています.')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']

        # データベース接続を取得
        conn = get_db_connection()
        cur = conn.cursor()

        # ユーザー名の重複をチェック
        cur.execute('SELECT * FROM Users WHERE name = %s', (username,))
        if cur.fetchone():
            # ユーザー名が既に存在する場合は、ユーザーに通知
            flash('このユーザー名は既に使用されています。別のユーザー名を選んでください。')
        else:
            # ユーザー情報をデータベースに挿入
            cur.execute('INSERT INTO Users (name, password) VALUES (%s, %s)',
                        (username, password))
            conn.commit()

            # 登録成功時にログインページにリダイレクト
            flash('新規登録が完了しました。ログインしてください。')
            return redirect(url_for('login'))

        # データベース接続を閉じる
        cur.close()
        conn.close()

    return render_template('register.html')

@app.route('/record', methods=['GET', 'POST'])
def record():
    # ログインしているユーザーのIDをセッションから取得
    user_id = session.get('user_id', None)

    # ユーザーがログインしていない場合はログインページにリダイレクト
    if not user_id:
        flash("ログインしてください。")
        return redirect(url_for('login'))

    # POST リクエストの処理: ユーザーが記録をデータベースに保存
    if request.method == 'POST':
        try:
            date = request.form['date']
            exercise = request.form['exercise']
            weight = request.form['weight']
            rep = request.form['rep']
            set_count = request.form['set']

            # データベース接続とデータ挿入
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('INSERT INTO Recorder (user_id, date, exercise, weight, rep, set) VALUES (%s, %s, %s, %s, %s, %s)',
                        (user_id, date, exercise, weight, rep, set_count))
            conn.commit()
            cur.close()
            conn.close()

            flash('トレーニング記録を保存しました。')
        except Exception as e:
            # エラーハンドリング
            flash('記録の保存中にエラーが発生しました。')
            print(e)

    # GET リクエストの処理: 記録入力フォームを表示
    return render_template('record.html')
@app.route('/home')
def home():
    if 'user_id' in session:
        user_id = session['user_id']  # セッションからユーザーIDを取得
        username = session['username']  # セッションからユーザー名を取得

        # データベースから最新のトレーニング記録を取得
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM recorder WHERE user_id = %s ORDER BY date DESC LIMIT 1;', (user_id,))
        latest_record = cur.fetchone()
        cur.close()
        conn.close()

        return render_template('home.html', latest_record=latest_record, username=username)
    return redirect(url_for('login'))
@app.route('/analyze')
def analyze():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT date, exercise, SUM(weight * rep * set) as total_weight FROM Recorder WHERE user_id = %s GROUP BY date, exercise ORDER BY date', (user_id,))
    records = cur.fetchall()
    cur.close()
    conn.close()

    # データを日付ごとに整理
    data_by_date = {}
    for record in records:
        date = record[0].strftime('%Y-%m-%d')
        if date not in data_by_date:
            data_by_date[date] = {}
        data_by_date[date][record[1]] = record[2]

    return render_template('analyze.html', data=data_by_date)

if __name__ == '__main__':
    app.run(debug=True)
