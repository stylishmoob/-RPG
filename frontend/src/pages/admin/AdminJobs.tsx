function AdminJobs(){
    return(
        <h2>職業管理</h2>

    <form method="POST" action="{{url_for('admin_add_jobs')}}">
        <input type="text" name="job_name" placeholder="職業名" required>
        <select name="status_id_1">
            {% for status in master_statuses %}
            <option value="{{status[0]}}">
                {{status[0]}}:{{status[1]}}:{{status[2]}}
            </option>
            {% endfor %}
        <input type="number" name="required_status1_value" placeholder="ステータス値1" required>
        <select name="status_id_2">
            {% for status in master_statuses %}
            <option value="{{status[0]}}">
                {{status[0]}}:{{status[1]}}:{{status[2]}}
            </option>
            {% endfor %}
        <input type="number" name="required_status2_value" placeholder="ステータス値2" required>
        <button type="submit">追加</button> 
    </form>

    <table border="1">
        <tr>
            <th>ID</th>
            <th>職業名</th>
            <th>ステータス名１</th>
            <th>必要ステータス値１</th>
            <th>ステータス名２</th>
            <th>必要ステータス値２</th>
        </tr>

        {% for id,job_name,status_name_1,requirement_status1_value,status_name_2,
                requirement_status2_value,is_active,is_default in master_jobs %}
        <tr>
            <td>{{id}}</td>
            <td>{{job_name}}</td>
            <td>{{status_name_1}}</td>
            <td>{{requirement_status1_value}}</td>
            <td>{{status_name_2}}</td>
            <td>{{requirement_status2_value}}</td>
            <td>{{is_default}}</td>
            <td>
            <form method="POST" action="{{url_for('admin_toggle_jobs')}}">
                <input type="hidden" name="job_id" value="{{id}}">
                {% if is_active %}
                <button type="submit">無効化</button>
                {% else %}
                <button type="submit">有効化</button>
                {% endif %}
            </form>
            </td>
        </tr>
        {% endfor %}
    </table>
    )
    
}
export default AdminJobs