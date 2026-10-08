import sqlite3
from datetime import date
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

DB='black_horse.db'
SPORTS=('Grappling','CrossFit')

def db():
    con=sqlite3.connect(DB); con.row_factory=sqlite3.Row; return con

def init():
    con=db(); con.executescript('''
    CREATE TABLE IF NOT EXISTS students(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,phone TEXT,sport TEXT NOT NULL,group_name TEXT,monthly_fee INTEGER DEFAULT 0,birth_date TEXT,subscription_until TEXT,active INTEGER DEFAULT 1);
    CREATE TABLE IF NOT EXISTS attendance(id INTEGER PRIMARY KEY AUTOINCREMENT,student_id INTEGER NOT NULL,att_date TEXT NOT NULL,present INTEGER NOT NULL,UNIQUE(student_id,att_date));
    CREATE TABLE IF NOT EXISTS payments(id INTEGER PRIMARY KEY AUTOINCREMENT,student_id INTEGER NOT NULL,pay_date TEXT NOT NULL,amount INTEGER NOT NULL,note TEXT);
    '''); con.commit(); con.close()

def popup(msg): Popup(title='Black Horse',content=Label(text=msg),size_hint=(.85,.35)).open()

KV='''
ScreenManager:
    Home:
    Students:
    Attendance:
    Payments:
    Reports:

<Home>:
    name:'home'
    BoxLayout: orientation:'vertical'; padding:18; spacing:12
    Label: text:'🐎 BLACK HORSE'; font_size:30; bold:True
    Label: text:'Sport klub boshqaruvi'; font_size:18
    Button: text:'👥 O‘quvchilar'; on_release: root.manager.current='students'
    Button: text:'📅 Davomat'; on_release: root.manager.current='attendance'
    Button: text:'💰 To‘lovlar'; on_release: root.manager.current='payments'
    Button: text:'📊 Hisobot'; on_release: root.manager.current='reports'

<Students>:
    name:'students'
    BoxLayout: orientation:'vertical'; padding:10; spacing:8
    BoxLayout: size_hint_y:None; height:50
        Button: text:'←'; size_hint_x:.18; on_release: root.manager.current='home'
        TextInput: id:search; hint_text:'Qidirish...'; on_text: root.refresh()
        Button: text:'+ O‘quvchi'; size_hint_x:.3; on_release: root.add()
    ScrollView:
        GridLayout: id:list; cols:1; spacing:6; size_hint_y:None; padding:3; height:self.minimum_height

<Attendance>:
    name:'attendance'
    BoxLayout: orientation:'vertical'; padding:10; spacing:8
    BoxLayout: size_hint_y:None; height:50
        Button: text:'←'; size_hint_x:.18; on_release: root.manager.current='home'
        Label: text:'DAVOMAT'; bold:True
        Button: text:'Yangilash'; size_hint_x:.3; on_release: root.refresh()
    ScrollView:
        GridLayout: id:list; cols:1; spacing:6; size_hint_y:None; height:self.minimum_height

<Payments>:
    name:'payments'
    BoxLayout: orientation:'vertical'; padding:10; spacing:8
    BoxLayout: size_hint_y:None; height:50
        Button: text:'←'; size_hint_x:.18; on_release: root.manager.current='home'
        Label: text:'TO‘LOVLAR'; bold:True
        Button: text:'+ To‘lov'; size_hint_x:.3; on_release: root.add()
    ScrollView:
        GridLayout: id:list; cols:1; spacing:6; size_hint_y:None; height:self.minimum_height

<Reports>:
    name:'reports'
    BoxLayout: orientation:'vertical'; padding:15; spacing:12
    Button: text:'←'; size_hint_y:None; height:50; on_release: root.manager.current='home'
    Label: id:text; text:'Hisobot'; font_size:18; halign:'left'; valign:'top'; text_size:self.width,None
'''

class Home(Screen): pass

class Students(Screen):
    def on_enter(self): self.refresh()
    def refresh(self):
        self.ids.list.clear_widgets(); q=self.ids.search.text.lower(); con=db()
        rows=con.execute('SELECT * FROM students WHERE active=1 ORDER BY name').fetchall(); con.close()
        for r in rows:
            if q and q not in r['name'].lower() and q not in (r['phone'] or '').lower(): continue
            b=BoxLayout(size_hint_y=None,height=75,spacing=5)
            from kivy.uix.button import Button
            info=Button(text=f"{r['name']}\n{r['sport']} | {r['group_name'] or '-'} | {r['monthly_fee']:,} so‘m",halign='left')
            info.bind(on_release=lambda x,r=r:self.profile(r['id']))
            b.add_widget(info); self.ids.list.add_widget(b)
    def add(self): self.form()
    def form(self,sid=None):
        layout=BoxLayout(orientation='vertical',padding=12,spacing=7)
        from kivy.uix.textinput import TextInput
        from kivy.uix.button import Button
        fields=[]
        for hint in ['F.I.Sh.','Telefon','Tug‘ilgan sana YYYY-MM-DD','Sport (Grappling/CrossFit)','Guruh','Oylik to‘lov','Abonement tugash YYYY-MM-DD']:
            x=TextInput(hint_text=hint,size_hint_y=None,height=42); fields.append(x); layout.add_widget(x)
        save=Button(text='Saqlash',size_hint_y=None,height=48); layout.add_widget(save)
        p=Popup(title='O‘quvchi',content=layout,size_hint=(.94,.9));
        if sid:
            con=db(); r=con.execute('SELECT * FROM students WHERE id=?',(sid,)).fetchone(); con.close()
            vals=[r['name'],r['phone'] or '',r['birth_date'] or '',r['sport'],r['group_name'] or '',str(r['monthly_fee']),r['subscription_until'] or '']
            for x,v in zip(fields,vals): x.text=v
        def saveit(*a):
            try: fee=int(fields[5].text.replace(' ','').replace(',','') or 0)
            except: popup('Oylik to‘lov raqam bo‘lishi kerak'); return
            if not fields[0].text.strip(): popup('F.I.Sh. kiriting'); return
            con=db(); vals=(fields[0].text,fields[1].text,fields[3].text or 'Grappling',fields[4].text,fee,fields[2].text,fields[6].text)
            if sid: con.execute('UPDATE students SET name=?,phone=?,sport=?,group_name=?,monthly_fee=?,birth_date=?,subscription_until=? WHERE id=?',vals+(sid,))
            else: con.execute('INSERT INTO students(name,phone,sport,group_name,monthly_fee,birth_date,subscription_until) VALUES(?,?,?,?,?,?,?)',vals)
            con.commit(); con.close(); p.dismiss(); self.refresh()
        save.bind(on_release=saveit); p.open()
    def profile(self,sid):
        con=db(); r=con.execute('SELECT * FROM students WHERE id=?',(sid,)).fetchone(); pays=con.execute('SELECT * FROM payments WHERE student_id=? ORDER BY pay_date DESC',(sid,)).fetchall(); att=con.execute('SELECT * FROM attendance WHERE student_id=? ORDER BY att_date DESC',(sid,)).fetchall(); con.close()
        s=f"{r['name']}\nSport: {r['sport']}\nGuruh: {r['group_name'] or '-'}\nTelefon: {r['phone'] or '-'}\nOylik: {r['monthly_fee']:,} so‘m\nAbonement: {r['subscription_until'] or '-'}\n\nTO‘LOVLAR:\n"
        s+='\n'.join(f"{x['pay_date']} — {x['amount']:,} so‘m" for x in pays) or '-'; s+='\n\nDAVOMAT:\n'; s+='\n'.join(f"{x['att_date']} — {'Keldi' if x['present'] else 'Kelmadi'}" for x in att) or '-'; popup(s)

class Attendance(Screen):
    def on_enter(self): self.refresh()
    def refresh(self):
        self.ids.list.clear_widgets(); con=db(); rows=con.execute('SELECT * FROM students WHERE active=1 ORDER BY name').fetchall(); con.close()
        from kivy.uix.button import Button
        for r in rows:
            b=Button(text=f"{r['name']} — {r['sport']}",size_hint_y=None,height=58); b.bind(on_release=lambda x,r=r:self.mark(r['id'],r['name'])); self.ids.list.add_widget(b)
    def mark(self,sid,name):
        con=db(); today=str(date.today()); old=con.execute('SELECT present FROM attendance WHERE student_id=? AND att_date=?',(sid,today)).fetchone(); con.close(); state=old['present'] if old else None
        from kivy.uix.button import Button
        l=BoxLayout(spacing=8,padding=12); p=Popup(title=name,content=l,size_hint=(.85,.3))
        for txt,val in [('✓ Keldi',1),('✕ Kelmadi',0)]:
            b=Button(text=txt); l.add_widget(b)
            def go(x,val=val):
                c=db(); c.execute('INSERT INTO attendance(student_id,att_date,present) VALUES(?,?,?) ON CONFLICT(student_id,att_date) DO UPDATE SET present=excluded.present',(sid,today,val)); c.commit(); c.close(); p.dismiss(); self.refresh()
            b.bind(on_release=go)
        p.open()

class Payments(Screen):
    def on_enter(self): self.refresh()
    def refresh(self):
        self.ids.list.clear_widgets(); con=db(); rows=con.execute('SELECT p.*,s.name FROM payments p JOIN students s ON s.id=p.student_id ORDER BY p.pay_date DESC,p.id DESC').fetchall(); con.close(); from kivy.uix.label import Label
        for r in rows: self.ids.list.add_widget(Label(text=f"{r['pay_date']} | {r['name']} | {r['amount']:,} so‘m",size_hint_y=None,height=50))
    def add(self): popup('To‘lov oynasi mobil versiyada tayyorlanmoqda.')

class Reports(Screen):
    def on_enter(self): self.refresh()
    def refresh(self):
        con=db(); total=con.execute('SELECT COUNT(*) n FROM students WHERE active=1').fetchone()['n']; g=con.execute("SELECT COUNT(*) n FROM students WHERE active=1 AND sport='Grappling'").fetchone()['n']; c=con.execute("SELECT COUNT(*) n FROM students WHERE active=1 AND sport='CrossFit'").fetchone()['n']; inc=con.execute('SELECT COALESCE(SUM(amount),0) n FROM payments').fetchone()['n']; today=str(date.today()); pres=con.execute('SELECT COUNT(*) n FROM attendance WHERE att_date=? AND present=1',(today,)).fetchone()['n']; exp=con.execute('SELECT COUNT(*) n FROM students WHERE active=1 AND subscription_until<>\'\' AND subscription_until < ?',(today,)).fetchone()['n']; con.close(); self.ids.text.text=f"Jami faol o‘quvchilar: {total}\n🥋 Grappling: {g}\n🏋️ CrossFit: {c}\n\nBugun kelganlar: {pres}\n💰 Jami to‘lovlar: {inc:,} so‘m\n🔴 Abonementi tugagan: {exp}"

class BlackHorse(App):
    def build(self): init(); return Builder.load_string(KV)

if __name__=='__main__': BlackHorse().run()
