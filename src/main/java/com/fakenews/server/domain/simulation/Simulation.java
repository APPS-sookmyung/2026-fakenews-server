package com.fakenews.server.domain.simulation;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;
import java.time.LocalDateTime;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Simulation {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(nullable = false)
    private Long ownerUserId;
    @Column(nullable = false, length = 100)
    private String name;
    @CreationTimestamp
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    public static Simulation create(Long ownerUserId, String name) {
        if (ownerUserId == null || ownerUserId <= 0 || name == null || name.isBlank() || name.strip().length() > 100) {
            throw new IllegalArgumentException("실험 소유자와 100자 이하의 실험 이름이 필요합니다.");
        }
        Simulation simulation = new Simulation();
        simulation.ownerUserId = ownerUserId;
        simulation.name = name.strip();
        return simulation;
    }
}
