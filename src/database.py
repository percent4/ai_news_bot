import os
import sqlite3
from typing import List, Dict, Any


class NewsDatabase:
    def __init__(self, db_path: str = None):
        """初始化数据库连接"""
        if db_path is None:
            # 检查是否存在data目录（Docker挂载目录）
            data_dir = os.path.join(os.path.dirname(__file__), 'data')
            if os.path.exists(data_dir):
                self.db_path = os.path.join(data_dir, 'ai_news.db')
            else:
                self.db_path = os.path.join(os.path.dirname(__file__), 'ai_news.db')
        else:
            self.db_path = db_path
        
        # 确保数据库目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """初始化数据库，创建ai_news表格"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建ai_news表格
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                tag TEXT NOT NULL,
                title TEXT NOT NULL,
                zh_title TEXT NOT NULL,
                link TEXT NOT NULL UNIQUE,
                content TEXT NOT NULL,
                summary TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("数据库和ai_news表格初始化完成")
    
    def insert_news(self, news_data: Dict[str, Any]) -> bool:
        """插入单条新闻数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO ai_news (date, tag, title, zh_title, link, content, summary)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                news_data.get('date'),
                news_data.get('tag'),
                news_data.get('title'),
                news_data.get('zh_title'),
                news_data.get('link'),
                news_data.get('content'),
                news_data.get('summary')
            ))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError as e:
            print(f"数据插入失败，链接可能已存在: {e}")
            return False
        except Exception as e:
            print(f"数据插入时发生错误: {e}")
            return False
    
    def insert_news_batch(self, news_list: List[Dict[str, Any]]) -> int:
        """批量插入新闻数据"""
        success_count = 0
        for news in news_list:
            if self.insert_news(news):
                success_count += 1
        
        print(f"成功插入 {success_count}/{len(news_list)} 条新闻数据")
        return success_count
    
    def get_news_by_date(self, date: str) -> List[Dict[str, Any]]:
        """根据日期获取新闻"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, date, title, link, content, summary, created_at
            FROM ai_news
            WHERE date = ?
            ORDER BY created_at DESC
        ''', (date,))
        
        rows = cursor.fetchall()
        conn.close()
        
        news_list = []
        for row in rows:
            news_list.append({
                'id': row[0],
                'date': row[1],
                'tag': row[2],
                'title': row[3],
                'zh_title': row[4],
                'link': row[5],
                'content': row[6],
                'summary': row[7],
                'created_at': row[6]
            })
        
        return news_list
    
    def get_all_news(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取所有新闻数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, date, tag, title, zh_title, link, content, summary, created_at
            FROM ai_news
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        news_list = []
        for row in rows:
            news_list.append({
                'id': row[0],
                'date': row[1],
                'tag': row[2],
                'title': row[3],
                'zh_title': row[4],
                'link': row[5],
                'content': row[6],
                'summary': row[7],
                'created_at': row[6]
            })
        
        return news_list
    
    def delete_news_by_id(self, news_id: int) -> bool:
        """根据ID删除新闻"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM ai_news WHERE id = ?', (news_id,))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                print(f"成功删除ID为 {news_id} 的新闻")
                return True
            else:
                conn.close()
                print(f"未找到ID为 {news_id} 的新闻")
                return False
        except Exception as e:
            print(f"删除新闻时发生错误: {e}")
            return False
    
    def get_news_count(self) -> int:
        """获取新闻总数"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM ai_news')
        count = cursor.fetchone()[0]
        
        conn.close()
        return count


if __name__ == '__main__':
    # 测试数据库功能
    db = NewsDatabase()
    print(f"当前数据库中有 {db.get_news_count()} 条新闻") 