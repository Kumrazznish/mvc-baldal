using System;
using System.Data;
using MySqlConnector;

namespace ShopManagement.DataAccess
{
    /// <summary>
    /// Lightweight, high-performance database helper for MySQL operations.
    /// Executes plain SQL text and Stored Procedures via ADO.NET and MySqlConnector.
    /// Stored Procedure definitions are maintained centrally in the master SQL setup script.
    /// </summary>
    public static class DbHelper
    {
        public static string ConnectionString { get; set; } = "Server=localhost;Database=ShopManagementDB;User ID=root;Password=root;Port=3306;AllowUserVariables=True;";

        public static MySqlConnection GetConnection()
        {
            var conn = new MySqlConnection(ConnectionString);
            if (conn.State != ConnectionState.Open)
            {
                conn.Open();
            }
            return conn;
        }

        public static DataTable ExecuteDataTable(string query, MySqlParameter[] parameters = null, CommandType commandType = CommandType.Text)
        {
            var dt = new DataTable();
            using (var conn = GetConnection())
            using (var cmd = new MySqlCommand(query, conn))
            {
                cmd.CommandType = commandType;
                if (parameters != null && parameters.Length > 0)
                {
                    cmd.Parameters.AddRange(parameters);
                }

                using (var adapter = new MySqlDataAdapter(cmd))
                {
                    adapter.Fill(dt);
                }
            }
            return dt;
        }

        public static int ExecuteNonQuery(string query, MySqlParameter[] parameters = null, CommandType commandType = CommandType.Text)
        {
            using (var conn = GetConnection())
            using (var cmd = new MySqlCommand(query, conn))
            {
                cmd.CommandType = commandType;
                if (parameters != null && parameters.Length > 0)
                {
                    cmd.Parameters.AddRange(parameters);
                }
                return cmd.ExecuteNonQuery();
            }
        }

        public static object ExecuteScalar(string query, MySqlParameter[] parameters = null, CommandType commandType = CommandType.Text)
        {
            using (var conn = GetConnection())
            using (var cmd = new MySqlCommand(query, conn))
            {
                cmd.CommandType = commandType;
                if (parameters != null && parameters.Length > 0)
                {
                    cmd.Parameters.AddRange(parameters);
                }
                return cmd.ExecuteScalar();
            }
        }

        #region Stored Procedure Convenience Helpers

        public static DataTable ExecuteStoredProcedureDataTable(string spName, MySqlParameter[] parameters = null)
        {
            return ExecuteDataTable(spName, parameters, CommandType.StoredProcedure);
        }

        public static int ExecuteStoredProcedureNonQuery(string spName, MySqlParameter[] parameters = null)
        {
            return ExecuteNonQuery(spName, parameters, CommandType.StoredProcedure);
        }

        public static object ExecuteStoredProcedureScalar(string spName, MySqlParameter[] parameters = null)
        {
            return ExecuteScalar(spName, parameters, CommandType.StoredProcedure);
        }

        #endregion

        /// <summary>
        /// Verifies database connectivity on application startup.
        /// Table schema, stored procedures, and triggers are deployed via the master SQL file.
        /// </summary>
        public static void InitializeDatabase()
        {
            try
            {
                using (var conn = GetConnection())
                {
                    // Simple connectivity test
                    using (var cmd = new MySqlCommand("SELECT 1;", conn))
                    {
                        cmd.ExecuteScalar();
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[DbHelper.InitializeDatabase] Warning: {ex.Message}");
            }
        }
    }
}
