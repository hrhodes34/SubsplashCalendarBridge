#!/usr/bin/env python3
"""
Calculate DST transition dates for 2025
"""

from datetime import datetime, timedelta

def get_nth_weekday_of_month(year: int, month: int, weekday: int, n: int) -> datetime:
    """Get the nth occurrence of a specific weekday in a given month"""
    # weekday: 0=Monday, 1=Tuesday, ..., 6=Sunday
    # n: which occurrence (1=first, 2=second, etc.)
    
    # Start with the first day of the month
    current_date = datetime(year, month, 1)
    
    # Find the first occurrence of the target weekday
    while current_date.weekday() != weekday:
        current_date += timedelta(days=1)
    
    # Add weeks to get to the nth occurrence
    current_date += timedelta(weeks=n-1)
    
    return current_date

def main():
    """Calculate DST dates for 2025"""
    year = 2025
    
    # DST start: second Sunday in March
    dst_start = get_nth_weekday_of_month(year, 3, 6, 2)  # 6 = Sunday, 2 = second occurrence
    
    # DST end: first Sunday in November
    dst_end = get_nth_weekday_of_month(year, 11, 6, 1)  # 6 = Sunday, 1 = first occurrence
    
    print(f"📅 DST Dates for {year}:")
    print(f"   DST starts: {dst_start.strftime('%Y-%m-%d')} (second Sunday in March)")
    print(f"   DST ends:   {dst_end.strftime('%Y-%m-%d')} (first Sunday in November)")
    
    # Test some specific dates
    test_dates = [
        ('2025-03-09', 'Day before DST starts'),
        ('2025-03-10', 'DST starts'),
        ('2025-11-02', 'Day before DST ends'),
        ('2025-11-03', 'DST ends'),
    ]
    
    print(f"\n🧪 Testing specific dates:")
    for date_str, description in test_dates:
        test_date = datetime.strptime(date_str, '%Y-%m-%d')
        is_dst = dst_start <= test_date < dst_end
        
        print(f"   {date_str}: {description}")
        print(f"      During DST: {is_dst}")
        print(f"      Offset: {4 if is_dst else 5} hours")

if __name__ == "__main__":
    main()
