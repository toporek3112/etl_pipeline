-- OLAP CUBES

-- Accidents by Time and Borough
SELECT
     t.year,
     t.month,
     d.borough,
     COUNT(a.accident_id) AS number_of_accidents
 FROM
     fact_accidents a
 JOIN dim_timestamps t ON a.timestamp_id = t.timestamp_id
 JOIN dim_addresses d ON a.address_id = d.address_id
 GROUP BY CUBE(t.year, t.month, d.borough)
 ORDER BY
     t.year DESC,
     t.month DESC, 
     d.borough DESC;

-- Accidents by Vehicle Type and Contributing Factor
SELECT
    v.vehicle_type,
    c.contributing_factor,
    COUNT(a.accident_id) AS number_of_accidents
FROM
    fact_accidents a
JOIN dim_vehicles v ON a.vehicle1_id = v.vehicle_id
JOIN dim_contributing_factors c ON a.contributing_factor1_id = c.contributing_factor_id
GROUP BY CUBE(v.vehicle_type, c.contributing_factor)
ORDER BY 
  c.contributing_factor ASC,
  number_of_accidents DESC,
  v.vehicle_type DESC;

-- Accidents by Contributing Factor and Borough
SELECT
    c.contributing_factor,
    d.borough,
    COUNT(a.accident_id) AS number_of_accidents
FROM
    fact_accidents a
JOIN dim_contributing_factors c ON a.contributing_factor1_id = c.contributing_factor_id
JOIN dim_addresses d ON a.address_id = d.address_id
GROUP BY CUBE(c.contributing_factor, d.borough)
ORDER BY 
  c.contributing_factor DESC,
  d.borough DESC,
  number_of_accidents ASC;

-- Accidents by Time and Vehicle Type
SELECT
    t.year,
    t.month,
    t.day,
    t.hour,
    v.vehicle_type,
    COUNT(a.accident_id) AS number_of_accidents
FROM
    fact_accidents a
JOIN dim_timestamps t ON a.timestamp_id = t.timestamp_id
JOIN dim_vehicles v ON a.vehicle1_id = v.vehicle_id
GROUP BY CUBE(t.hour, t.day, t.month, t.year, v.vehicle_type)
ORDER BY
    t.year DESC,
    t.month DESC,
    t.day DESC,
    t.hour DESC,
    v.vehicle_type DESC,
    number_of_accidents DESC;
