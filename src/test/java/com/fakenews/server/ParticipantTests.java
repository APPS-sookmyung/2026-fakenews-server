package com.fakenews.server;

import com.fakenews.server.domain.participant.entity.Participant;
import jakarta.persistence.EntityManager;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

@SpringBootTest
@Transactional
class ParticipantTests {
    @Autowired EntityManager entityManager;

    @Test
    void persistsPersonaWithoutLoginAccountAndUpdatesInterests() {
        Participant participant = Participant.create(1L, null, " 독서가 ",
                "주말에 도서관을 이용하며 지역 소식에 관심이 많음", List.of(" 독서 ", "독서", "지역 소식"));
        entityManager.persist(participant);
        entityManager.flush();
        Long id = participant.getId();
        entityManager.clear();

        Participant saved = entityManager.find(Participant.class, id);
        assertThat(saved.getSimulationId()).isEqualTo(1L);
        assertThat(saved.getUserId()).isNull();
        assertThat(saved.getDisplayName()).isEqualTo("독서가");
        assertThat(saved.getDescription()).contains("도서관");
        assertThat(saved.getInterests()).containsExactlyInAnyOrder("독서", "지역 소식");
        assertThat(saved.getCreatedAt()).isNotNull();
        assertThat(saved.getUpdatedAt()).isNotNull();

        saved.updateProfile("새 이름", "새 성향", List.of("과학"));
        entityManager.flush();
        entityManager.clear();
        assertThat(entityManager.find(Participant.class, id).getInterests()).containsExactly("과학");
    }

    @Test
    void keepsExistingProfileWhenUpdateIsInvalid() {
        Participant participant = Participant.create(1L, 2L, "참여자", "성향", List.of("독서"));
        assertThat(participant.getUserId()).isEqualTo(2L);
        assertThatThrownBy(() -> participant.updateProfile("새 이름", "새 설명", List.of(" ")))
                .isInstanceOf(IllegalArgumentException.class);
        assertThat(participant.getDisplayName()).isEqualTo("참여자");
        assertThat(participant.getDescription()).isEqualTo("성향");
        assertThat(participant.getInterests()).containsExactly("독서");
        assertThatThrownBy(() -> participant.getInterests().add("과학"))
                .isInstanceOf(UnsupportedOperationException.class);
    }

    @Test
    void rejectsMissingPersonaAndInvalidIdentifiers() {
        assertThatThrownBy(() -> Participant.create(null, null, "이름", "성향", List.of()))
                .isInstanceOf(IllegalArgumentException.class);
        assertThatThrownBy(() -> Participant.create(1L, 0L, "이름", "성향", List.of()))
                .isInstanceOf(IllegalArgumentException.class);
        assertThatThrownBy(() -> Participant.create(1L, null, " ", "성향", List.of()))
                .isInstanceOf(IllegalArgumentException.class);
        assertThatThrownBy(() -> Participant.create(1L, null, "이름", " ", List.of()))
                .isInstanceOf(IllegalArgumentException.class);
        assertThatThrownBy(() -> Participant.create(1L, null, "이름", "성향", List.of("a".repeat(101))))
                .isInstanceOf(IllegalArgumentException.class);
    }
}
