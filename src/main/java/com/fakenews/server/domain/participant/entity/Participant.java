package com.fakenews.server.domain.participant.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import jakarta.validation.constraints.Size;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;
import java.util.Collection;
import java.util.Collections;
import java.util.LinkedHashSet;
import java.util.Set;

@Entity
@Table(uniqueConstraints = @UniqueConstraint(name = "uk_participant_simulation_user", columnNames = {"simulation_id", "user_id"}))
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Participant {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // 소속 실험 ID. 로그인 사용자 ID와 구분하며 등록 API에서 실험 소유권을 확인한다.
    @NotNull
    @Positive
    @Column(name = "simulation_id", nullable = false)
    private Long simulationId;

    // 로그인 계정에 연결되지 않은 시뮬레이션 참여자는 null이다.
    @Positive
    @Column(name = "user_id")
    private Long userId;

    @NotBlank
    @Size(max = 50)
    @Column(nullable = false, length = 50)
    private String displayName;

    // PlanningAgent의 profile.description에 전달할 페르소나·성향 설명.
    @NotBlank
    @Size(max = 5000)
    @Column(nullable = false, length = 5000)
    private String description;

    @ElementCollection
    @CollectionTable(name = "participant_interest", joinColumns = @JoinColumn(name = "participant_id"))
    @Column(name = "interest", nullable = false, length = 100)
    @Getter(AccessLevel.NONE)
    private Set<@NotBlank @Size(max = 100) String> interests = new LinkedHashSet<>();

    @CreationTimestamp
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(nullable = false)
    private LocalDateTime updatedAt;

    public static Participant create(Long simulationId, Long userId, String displayName,
                                     String description, Collection<String> interests) {
        if (simulationId == null || simulationId <= 0) {
            throw new IllegalArgumentException("실험 ID는 양수여야 합니다.");
        }
        if (userId != null && userId <= 0) {
            throw new IllegalArgumentException("사용자 ID는 양수여야 합니다.");
        }
        Participant participant = new Participant();
        participant.simulationId = simulationId;
        participant.userId = userId;
        participant.updateProfile(displayName, description, interests);
        return participant;
    }

    public void updateProfile(String displayName, String description, Collection<String> interests) {
        String nextName = requiredText(displayName, 50, "표시 이름");
        String nextDescription = requiredText(description, 5000, "성향 설명");
        if (interests == null) {
            throw new IllegalArgumentException("관심사는 빈 목록 또는 값이 있는 목록이어야 합니다.");
        }
        Set<String> nextInterests = new LinkedHashSet<>();
        for (String interest : interests) {
            nextInterests.add(requiredText(interest, 100, "관심사"));
        }
        this.displayName = nextName;
        this.description = nextDescription;
        this.interests.clear();
        this.interests.addAll(nextInterests);
    }

    public Set<String> getInterests() {
        return Collections.unmodifiableSet(interests);
    }

    private static String requiredText(String value, int maxLength, String field) {
        if (value == null || value.isBlank() || value.strip().length() > maxLength) {
            throw new IllegalArgumentException(field + "은(는) 공백이 아니고 " + maxLength + "자 이하여야 합니다.");
        }
        return value.strip();
    }
}
